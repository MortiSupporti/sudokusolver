"""Contains functions for image recognition and manipulation
table of content:
    load_image
        resize_loaded_image
    image_proc_routine
        image_processing
            preprocessing_image UNUSED
            cropping_image
            scaling_image
            proc_cropped_image
            visualizing_current_image_processing
            formatting_sudoku_matrix
        identify_grid
            get_contours_filtered
            repair_lines
    draw_output_image
        draw_number
    save_output_image
    display_image_and_wait"""

import cv2
import pytesseract as tes
import numpy as np
from imutils import contours, convenience

def load_image(image_path):
    """load_image(image_path)
    -> loaded_image

    loads image and adjusts size"""
    loaded_image = cv2.imread(image_path)
    height, width, _ = loaded_image.shape
    if height < 450 or height > 600 or width < 450 or width > 600:
        return resize_loaded_image(loaded_image)
    return loaded_image

def resize_loaded_image(input_image, target_size=550):
    """resize_loaded_image(input_image, target_size)
    -> resized_image
    defaults: target_size=550

    part of load_image
    changes size so that the shorter image length becomes the target_size"""
    height, width, _ = input_image.shape
    if height < width:
        return convenience.resize(input_image, height=target_size)
    else:
        return convenience.resize(input_image, width=target_size)

def display_image_and_wait(input_image):
    """display_image_and_wait()
    -> None

    displays image and waits forever"""
    cv2.imshow("RESULT", input_image)
    cv2.waitKey()
    return

def image_proc_routine(input_image, ausgabe_parameter=None):
    """image_proc_routine(input_image, ausgabe_parameter)
    -> tuple of (sudoku_matrix, coor_list, input_image)
    defaults: ausgabe_parameter=None

    requires image as input, use png!
    tuple contains: [0] empty sudoku matrix [1] list of coordinates [2] input_image
    detects grid and reads numbers"""
    sudoku_matrix, coor_list = image_processing(input_image, 0, False) # suggestion 150 True
    if ausgabe_parameter == "Ausgabe":
        for row in sudoku_matrix:
            print(row)
    return (sudoku_matrix, coor_list, input_image)

## combines all processing of the input_image
def image_processing(input_image, visualizing_time=0, with_mask=False):
    """image_processing(input_image, visualizing_time, with_mask)
    -> tuple of sudoku_matrix, coor_list
    defaults: visualizing_time=0, with_mask=False
    optional: can visualize mask and single boxes

    main process, combines processing of imput_image
    identifies grid and each single box
    creates a mask to read single boxes
    saves coordinate for each box
    saves sudoku_matrix, numbers are numbers and spaces are zeroes"""
    sudoku_matrix = []
    grid_data = identify_grid(input_image)

    ## Jede Kontur wird genutzt um eine Maske zu erstellen
    ## Es wird über die Matrix der Konturen iteriert
    ## Das input_image wird maskiert und Tesseract übergeben
    ## Der Tesseract-Output wird in einer string Matrix gespeichert
    ## creates a list of proper coordinates
    coor_list = []
    for row in grid_data: #for (i, row) in enumerate(grid_data, start=0):
        next_row = []
        for single_contour in row: #for (j, single_contour) in enumerate(row, start=0):
            mask = np.zeros(input_image.shape, dtype=np.uint8)
            cv2.drawContours(mask, [single_contour], -1, (255,255,255), -1)
            result = cv2.bitwise_and(input_image, mask)
            result[mask==0] = 255 #macht alles weiß, wo die maske 0 ist
            if len(single_contour) == 4:
                coor = np.concatenate(single_contour[0:3:2]).ravel().tolist() 
    ## holt die obere linke und untere rechte koordinate, entfernt unnötiges nestig, cast zu liste
            else:
                bounding_c = cv2.boundingRect(single_contour)
                coor = [bounding_c[0], bounding_c[1], bounding_c[0]+bounding_c[2], bounding_c[1]+bounding_c[3]]
            coor_list.append(coor)
            result = cropping_image(result, coor)
            result = scaling_image(result)
            result = proc_cropped_image(result)

            visualizing_current_image_processing(result, mask, visualizing_time, with_mask)

            next_row.append(tes.image_to_string(result, config="--psm 10"))

        sudoku_matrix.append(next_row)
    sudoku_matrix = formatting_sudoku_matrix(sudoku_matrix, "int")

    return sudoku_matrix, coor_list

def identify_grid(input_image):
    """identify_grid(input_image)
    -> grid data (coordinates of boxes)

    identifies grid by filtering everything but the grid
    then repairing maybe broken grid lines
    then outputting coordinates of each box inside the grid
    returns a matrix with the coordinates of each box
    9x9x4 9 rows, 9 columns, 4 coordinates for the box"""
    ## blurring
    blurred_image = cv2.GaussianBlur(input_image,(3,3),0)

    ## greyscaling
    ## macht Bild schwarz-weiß
    greyscale_image = cv2.cvtColor(blurred_image, cv2.COLOR_BGR2GRAY)

    ## thresholding, adaptive with gauss
    ## setzt Pixel auf 0 oder 255 wenn eine Schwelle überschritten wird, Adaptiv.
    threshold_image = cv2.adaptiveThreshold(greyscale_image,255,cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV,5,1)

    ## filtering out numbers and noise to detect boxes
    ## filtert alle nummern und anderen kram raus, nur gitter.
    contours_of_image = cv2.findContours(threshold_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours_of_image = contours_of_image[0] if len(contours_of_image) == 2 else contours_of_image[1]
    for ele in contours_of_image:
        area = cv2.contourArea(ele)
        if area < 1000:
            cv2.drawContours(threshold_image, [ele], -1, (0,0,0), -1)

    ## repairs horizontal and vertical lines
    ## inverts repaired image, so it fits our later masking
    ## moved process into a function for reusability in later loop
    ## successfull contours will be exactly 81 because 9*9
    inverted_repaired_image = repair_lines(threshold_image, 9, invert=True)
    contours_of_image = get_contours_filtered(inverted_repaired_image)
    ## adjusts repair process if we detect a different amount of contours
    ## contours need to be 81
    ## else the process changes the iterations of eroding and dilating
    ##
    ## RICEFIELD ausgang einbauen falls wir nie 81 finden
    ## --- missing currently --- error exist if we completly fail
    repair_iter_counter = 2
    while(len(contours_of_image)) != 81:
        inverted_repaired_image = repair_lines(threshold_image, repair_iter_counter, invert=True)
        contours_of_image = get_contours_filtered(inverted_repaired_image)
        repair_iter_counter += 1
        if repair_iter_counter == 100:
            #RICEFIELD EXCEPTION HANDLING
            print("ERROR GRID NOT IDENTIFIED")
            return

    ## sorts contours for our matrix
    ## first we sort by left and right within a row
    ## second we invert the order of the rows so upside-down gets fixed
    sudoku_rows = []
    row = []
    for (i, single_contour) in enumerate(contours_of_image, start=1):
        row.append(single_contour)
        if i % 9 == 0:
            (contours_of_image, _) = contours.sort_contours(row, method="left-to-right")
            ## hier bereits richtig von l nach r
            sudoku_rows.append(contours_of_image)
            row = []
    sudoku_rows.reverse() ## sortiert hiermit richtiv von o nach u


    return sudoku_rows

def visualizing_current_image_processing(single_box, mask, visualizing_time, with_mask):
    """visualizing_current_image_processing(single_box, mask, visualizing_time, with_mask)
    -> None

    OPTIONAL FUNCTION
    suggested time 250
    visualizes single steps of image processing
    can show the mask and can show the current sudoku box"""
    if visualizing_time == 0:
        return
    cv2.imshow("Current grid box", single_box)
    if with_mask == True:
        cv2.imshow("Current mask", mask)
    cv2.waitKey(visualizing_time)
    return

def preprocessing_image(input_image):
    """UNUSED"""
    return

def cropping_image(input_image, coordinates, borderless=True, border_value=2):
    """cropping_image(input_image, coordinates, borderless, border_value)
    -> cropped_image
    defaults: borderless=True, border_value=2

    part of image_processing
    crops an image
    coordinates has to be this format (x_start, x_end, y_start, y_end)
    coordinates[0] = x_start     coordinates[2] = x_end
    coordinates[1] = y_start     coordinates[3] = y_end"""
    if borderless == True:
        bordered_coor = (coordinates[0]+border_value, coordinates[1]+border_value, coordinates[2]-border_value, coordinates[3]-border_value)
        cropped_image = input_image[bordered_coor[1]:bordered_coor[3], bordered_coor[0]:bordered_coor[2]]
    elif borderless == False:
        cropped_image = input_image[coordinates[1]:coordinates[3], coordinates[0]:coordinates[2]]
        return cropped_image
    else:
        cropped_image = input_image[coordinates[1]:coordinates[3], coordinates[0]:coordinates[2]]
        return cropped_image
    return cropped_image

def scaling_image(input_image, scaling_factor=2, interpolation=cv2.INTER_AREA):
    """scaling_image(input_image, scaling_factor, interpolation)
    -> resized_image
    defaults: scaling_factor=2, interpolation=cv2.INTER_AREA

    upscales or downscales an image, part of image_processing
    by default upscale, doubles width and height"""
    width = int(input_image.shape[1] * scaling_factor)
    height = int(input_image.shape[0] * scaling_factor)
    dimensions = (width, height)
    resized_image = cv2.resize(input_image, dimensions, interpolation=interpolation)
    return resized_image

def proc_cropped_image(input_image, kernel=np.ones((3,3),np.uint8)):
    """proc_cropped_image(input_image, kernel)
    ->
    defaults: kernel = np.ones((3,3),np.uint8)

    part of image_processing
    processes the image of a single box that was scaled and procced before
    grey, blurr, denoise, threshold, invert, dilate, invert back
    """
    grey_image = cv2.cvtColor(input_image, cv2.COLOR_BGR2GRAY)
    blurred_grey_image = cv2.medianBlur(grey_image, 5)
    denoised_image = cv2.fastNlMeansDenoising(blurred_grey_image, h=10)
    threshold_image = cv2.adaptiveThreshold(denoised_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,11,5)
    dilated_image = cv2.dilate(255-threshold_image, kernel, iterations=2)
    inv_dilated_image = 255-dilated_image
    return inv_dilated_image

def repair_lines(input_image, iterations, v_kernel_size=(1,5), h_kernel_size=(5,1), invert=True):
    """repair_lines(input_image, iterations, v_kernel_size, h_kernel_size, invert=True)
    -> repaired_image
    defaults: v_kernel_size=(1,5), h_kernel_size=(5,1), invert=True

    part of identify_grid
    strengthens lines my morphing up and down
    repairs grid"""
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, v_kernel_size)
    repaired_image = cv2.morphologyEx(input_image, cv2.MORPH_CLOSE, vertical_kernel, iterations=iterations)
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, h_kernel_size)
    repaired_image = cv2.morphologyEx(repaired_image, cv2.MORPH_CLOSE, horizontal_kernel, iterations=iterations)
    if invert == True:
        return 255-repaired_image
    return repaired_image

def get_contours_filtered(input_image):
    """get_contours_filtered(input_image)
    -> contours_of_image

    part of identify_grid
    gets contours
    can adjust index of contours"""
    contours_of_image = cv2.findContours(input_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours_of_image = contours_of_image[0] if len(contours_of_image) == 2 else contours_of_image[1]
    return contours_of_image

def formatting_sudoku_matrix(input_matrix, outputtype="int"):
    """formatting_sudoku_matrix(input_matrix, outputtype)
    -> filtered_matrix
    defaults: outputtype="int"

    pytesseracts gives unwanted symbols
    filters these symbols and formats the output to desired type"""
    filtered_matrix = []
    for i in input_matrix:
        next_row = []
        for j in i:
            next_number = "".join(x if x.isnumeric() else "" for x in j)
            next_row.append(next_number if next_number != "" else "0")
        filtered_matrix.append(next_row)

    if outputtype == "string":
        return filtered_matrix

    elif outputtype == "int":
        int_filtered_matrix = []
        for i in filtered_matrix:
            int_filtered_matrix.append([int(x) for x in i])
        return int_filtered_matrix

    else:
        return filtered_matrix

def draw_output_image(input_image, coor_list, original_matrix, solved_matrix):
    """draw_output_image(input_image, coor_list, original_matrix, solved_matrix)
    -> output_image

    creates new image of solved sudoku
    calls repeatedly draw_number()"""
    output_image = input_image
    coor_index = 0
    counter_i_solved_matrix = 0
    for row in original_matrix:
        counter_j_solved_matrix = 0
        for field in row:
            if int(field) == 0:
                output_image = draw_number(output_image, coor_list[coor_index], solved_matrix[counter_i_solved_matrix][counter_j_solved_matrix])
            coor_index += 1
            counter_j_solved_matrix += 1
        counter_i_solved_matrix += 1
    return output_image

def draw_number(input_image, coor, number):
    """draw_number(input_image, coor, number)
    -> output_image

    part of draw_output_image
    draws one number on the input_image"""
    bottom_left = False ## if False, then top_left
    start_coor = (coor[0], coor[1]) if bottom_left else (coor[0], coor[3])
    font_type = cv2.FONT_HERSHEY_SIMPLEX
    font_scale_factor = 2
    font_color = (0, 255, 0)
    font_thickness = 2
    line_type = cv2.LINE_AA
    output_image = cv2.putText(input_image, str(number), start_coor, font_type, font_scale_factor, font_color, font_thickness, line_type, bottom_left)

    return output_image

def save_output_image(output_image, image_path_w_name="images/last_solved_image.png"):
    """save_output_image(output_image, image_path)
    -> None
    defaults: image_path="images/last_solved_image.png"

    saves image of solved sudoku to file system"""
    cv2.imwrite(image_path_w_name, output_image)
    return
