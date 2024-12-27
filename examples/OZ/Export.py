import csv
import numpy as np
from PIL import Image, ImageDraw

def export(root_node, path):
    with open(path + "oz.csv", "w") as f:
        f.write(str(root_node.get_child_n("field").get_parameter_n("vegetable").values[0]) + "\n")

        nb_row = root_node.get_child_n("field").get_child_n("row").nb_instances
        f.write(str(nb_row) + "\n")
        length = ""
        noise_X = ""
        noise_Y = ""
        disappearance_probability = ""
        vegetable_density = ""
        
        for i in range(nb_row):
            length += str(root_node.get_child_n("field").get_child_n("row").get_parameter_n("length", i).values[0]) + ";"
            noise_X += str(root_node.get_child_n("field").get_child_n("row").get_parameter_n("noise_X", i).values[0]) + ";"
            noise_Y += str(root_node.get_child_n("field").get_child_n("row").get_parameter_n("noise_Y", i).values[0]) + ";"
            disappearance_probability += str(root_node.get_child_n("field").get_child_n("row").get_parameter_n("disappearance_probability", i).values[0]) + ";"
            vegetable_density += str(root_node.get_child_n("field").get_child_n("row").get_parameter_n("vegetable_density", i).values[0]) + ";"
        f.write(length[:-1] + "\n")
        f.write(noise_X[:-1] + "\n")
        f.write(noise_Y[:-1] + "\n")
        f.write(disappearance_probability[:-1] + "\n")
        f.write(vegetable_density[:-1] + "\n")
        
        nb_weed_area = root_node.get_child_n("field").get_child_n("weed_area").nb_instances
        f.write(str(nb_weed_area) + "\n")
        grass_density = ""
        for i in range(nb_weed_area):
            grass_density += str(root_node.get_child_n("field").get_child_n("weed_area").get_parameter_n("grass_density", i).values[0]) + ";"
        f.write(grass_density[:-1] + "\n")

        if root_node.get_child_n("field").get_child_n("inner_track_width") == None:
            f.write("0\n\n")
        else:
            nb_inner_track_width = root_node.get_child_n("field").get_child_n("inner_track_width").nb_instances
            f.write(str(nb_inner_track_width) + "\n")
            gap = ""
            for i in range(nb_inner_track_width):
                gap += str(root_node.get_child_n("field").get_child_n("inner_track_width").get_parameter_n("gap", i).values[0]) + ";"
            f.write(gap[:-1] + "\n")

        f.write(str(root_node.get_child_n("mission").get_parameter_n("two_pass").values[0]) + "\n")
        f.write(str(root_node.get_child_n("mission").get_parameter_n("is_first_track_outer").values[0]) + "\n")
        f.write(str(root_node.get_child_n("mission").get_parameter_n("final_track_outer").values[0]) + "\n")
        f.write(str(root_node.get_child_n("mission").get_parameter_n("is_track_side_at_left").values[0]) + "\n")
        f.write(str(root_node.get_child_n("mission").get_parameter_n("is_first_uturn_right_side").values[0]) + "\n")

        f.write(str(root_node.get_child_n("terrain").get_child_n("heightmap").get_parameter_n("roughness").values[0]) + "\n")
        f.write(str(root_node.get_child_n("terrain").get_child_n("heightmap").get_parameter_n("persistence").values[0]) + "\n")
    generate_image(read_csv(path + "oz.csv"), path + "champ.jpg")

def read_csv(path):
    with open(path, newline='') as csvfile:
        data = list(csv.reader(csvfile))
    
    vegetable = data[0][0]
    nb_row = int(data[1][0])
    lengths = list(map(float, data[2][0].split(';')))
    noise_X = list(map(float, data[3][0].split(';')))
    noise_Y = list(map(float, data[4][0].split(';')))
    disappearance_probability = list(map(float, data[5][0].split(';')))
    vegetable_density = list(map(int, data[6][0].split(';')))
    
    nb_weed_area = int(data[7][0])
    grass_density = list(map(int, data[8][0].split(';')))
    
    nb_inner_track_width = int(data[9][0])
    gap = list(map(int, data[10][0].split(';')))
    
    mission_params = {
        "two_pass": data[11][0] == 'True',
        "is_first_track_outer": data[12][0] == 'True',
        "final_track_outer": data[13][0] == 'True',
        "is_track_side_at_left": data[14][0] == 'True',
        "is_first_uturn_right_side": data[15][0] == 'True'
    }
    
    roughness = float(data[16][0])
    persistence = float(data[17][0])
    
    return {
        "vegetable": vegetable,
        "nb_row": nb_row,
        "lengths": lengths,
        "noise_X": noise_X,
        "noise_Y": noise_Y,
        "disappearance_probability": disappearance_probability,
        "vegetable_density": vegetable_density,
        "nb_weed_area": nb_weed_area,
        "grass_density": grass_density,
        "nb_inner_track_width": nb_inner_track_width,
        "gap": gap,
        "mission_params": mission_params,
        "roughness": roughness,
        "persistence": persistence
    }

def generate_image(data, path):
    width = 1000
    height = 500
    img = Image.new('RGB', (width, height), "white")
    pixels = img.load()
    draw = ImageDraw.Draw(img)
    
    nb_row = data['nb_row']
    lengths = data['lengths']
    noise_X = data['noise_X']
    noise_Y = data['noise_Y']
    roughness = data['roughness']
    persistence = data['persistence']
    
    max_length = max(lengths)
    min_length = min(lengths)
    
    for i in range(nb_row):
        row_length = lengths[i]
        row_width = int((row_length / max_length) * width)
        row_height = int((height / nb_row) * (1 - (noise_Y[i] / 5)))
        y_position = int((i * height / nb_row) * (1 + (noise_X[i] / 5)))
        
        color_intensity = int((row_length - min_length) / (max_length - min_length) * 255)
        color = (color_intensity, 100, 100)
        
        for x in range(row_width):
            for y in range(row_height):
                if 0 <= x < width and 0 <= y_position + y < height:
                    pixels[x, y_position + y] = color
    
    draw.text((10, 10), f"Type de légume : {data['vegetable']}", fill=(0, 0, 0))
    draw.text((10, 30), f"Nombre de rangées : {nb_row}", fill=(0, 0, 0))
    draw.text((10, 50), f"Roughness : {roughness}", fill=(0, 0, 0))
    draw.text((10, 70), f"Persistence : {persistence}", fill=(0, 0, 0))
    draw.text((10, 90), "Légende :", fill=(0, 0, 0))
    draw.text((30, 110), "Rangées de légumes", fill=(255, 100, 100))
    draw.text((30, 130), "Zones de mauvaises herbes", fill=(0, 255, 0))
    draw.text((30, 150), "Pistes intérieures", fill=(0, 0, 255))

    img.save(path)
    
