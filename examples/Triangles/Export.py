import math
import matplotlib.pyplot as plt

def export(root_node, path):
	# exportv1(root_node, path)
	# exportv2(root_node, path)
	enfants=root_node.get_children()
	if(enfants[-1]=="triangleIsoceles"):
		exportv2(root_node, path)
	elif(enfants[-1]=="triangleRectangle"):
		export_triangle(root_node, path)

def exportv1(root_node, path):
	points_node = root_node.get_child_n("triangleIsoceles").get_container_i(0)
	points = []
	nomPoints = ["pointA", "pointB", "pointC"]
	for point in nomPoints:
		x = int(points_node.get_child_n(point).get_parameter_n("x").values[0])
		y = int(points_node.get_child_n(point).get_parameter_n("y").values[0])
		points.append((x, y))

	fig, ax = plt.subplots()
	ax.grid(True)
	triangle_patch = plt.Polygon(points, closed=True, fill=None, edgecolor='black')
	ax.add_patch(triangle_patch)

	min_x = min([point[0] for point in points])
	max_x = max([point[0] for point in points])
	min_y = min([point[1] for point in points])
	max_y = max([point[1] for point in points])
	ax.set_xlim(min_x - 10, max_x + 10)
	ax.set_ylim(min_y - 10, max_y + 10)

	ax.set_xlabel('X')
	ax.set_ylabel('Y')
	ax.set_title('Triangle' + is_isosceles_triangle(points))

	plt.savefig(path + "graphe.jpg", format='jpg')


def exportv2(root_node, path):
	fig, ax = plt.subplots()
	triangle_node = root_node.get_child_n("triangleIsoceles").get_child_n("point")

	points = []
	for i in range(triangle_node.get_nb_instances()):
		point_node = triangle_node.get_container_i(i)
		x = int(point_node.get_parameter_n("x").values[0])
		y = int(point_node.get_parameter_n("y").values[0])
		points.append((x, y))

	ax.grid(True)
	triangle_patch = plt.Polygon(points, closed=True, fill=None, edgecolor='black')
	ax.add_patch(triangle_patch)


	min_x = min([point[0] for point in points])
	max_x = max([point[0] for point in points])
	min_y = min([point[1] for point in points])
	max_y = max([point[1] for point in points])
	ax.set_xlim(min_x - 10, max_x + 10)
	ax.set_ylim(min_y - 10, max_y + 10)
	ax.set_xlabel('X')
	ax.set_ylabel('Y')
	ax.set_title('Triangle' + is_isosceles_triangle(points))
	ax.set_aspect('equal')
	plt.savefig(path + "graphe.jpg", format='jpg')

def is_isosceles_triangle(points):
	x1, y1 = points[0]
	x2, y2 = points[1]
	x3, y3 = points[2]
	side1_squared = (x2 - x1) ** 2 + (y2 - y1) ** 2
	side2_squared = (x3 - x1) ** 2 + (y3 - y1) ** 2
	side3_squared = (x3 - x2) ** 2 + (y3 - y2) ** 2

	if side1_squared == side2_squared or side1_squared == side3_squared or side2_squared == side3_squared:
		return " qui est isocèle"
	else:
		return " qui n'est PAS isocèle"
	
def calculate_angle(a, b, c):
    return math.acos((b**2 + c**2 - a**2) / (2 * b * c))

def annotate_triangle(points, ax):
    a = math.sqrt((points[1][0] - points[0][0])**2 + (points[1][1] - points[0][1])**2)
    b = math.sqrt((points[2][0] - points[1][0])**2 + (points[2][1] - points[1][1])**2)
    c = math.sqrt((points[2][0] - points[0][0])**2 + (points[2][1] - points[0][1])**2)

    angle_B = calculate_angle(c, a, b)
    angle_B = math.degrees(angle_B)
    ax.text(points[1][0], points[1][1], f"{angle_B:.1f}°", ha="center", va="center")

def export_triangle(root_node, path):
    fig, ax = plt.subplots()
    triangle_node = root_node.get_child_n("triangleRectangle").get_child_n("point")

    points = []
    for i in range(triangle_node.get_nb_instances()):
        point_node = triangle_node.get_container_i(i)
        x = int(point_node.get_parameter_n("x").values[0])
        y = int(point_node.get_parameter_n("y").values[0])
        points.append((x, y))

    ax.grid(True)
    triangle_patch = plt.Polygon(points, closed=True, fill=None, edgecolor="black")
    ax.add_patch(triangle_patch)

    annotate_triangle(points, ax)
    min_x = min([point[0] for point in points])
    max_x = max([point[0] for point in points])
    min_y = min([point[1] for point in points])
    max_y = max([point[1] for point in points])
    ax.set_xlim(min_x - 10, max_x + 10)
    ax.set_ylim(min_y - 10, max_y + 10)
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_title("Triangle rectangle")
    ax.set_aspect("equal")
    plt.savefig(path + "graphe.jpg", format="jpg")
