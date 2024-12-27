import matplotlib.pyplot as plt
import numpy as np

def temps_entree_sortie_rayon_5(x, y, v):
	distance = np.sqrt(x**2 + y**2) 
	temps_entree = (distance - 5)/ v  
	temps_sortie = (distance + 5)/ v
	return temps_entree, temps_sortie

def export(root_node, path):
	fig, ax = plt.subplots()

	points = []

	graphe_node = root_node.get_child_n("graphe")
	pointA_node = graphe_node.get_child_n("point").get_container_i(0)
	xA = int(pointA_node.get_parameter_n("x").values[0])
	yA = int(pointA_node.get_parameter_n("y").values[0])
	vA = int(pointA_node.get_parameter_n("v").values[0])
	points.append((xA, yA))

	pointB_node = graphe_node.get_child_n("point").get_container_i(1)
	xB = int(pointB_node.get_parameter_n("x").values[0])
	yB = int(pointB_node.get_parameter_n("y").values[0])
	vB = int(pointB_node.get_parameter_n("v").values[0])
	points.append((xB, yB))

	points.append((0, 0))

	dirA = np.array([0 - xA, 0 - yA])
	dirB = np.array([0 - xB, 0 - yB])
	dirA = dirA / np.linalg.norm(dirA)
	dirB = dirB / np.linalg.norm(dirB)


	x_traj_A, y_traj_A = [], []
	for t in range(50): 
		x_traj_A.append(xA + t * dirA[0] * vA)
		y_traj_A.append(yA + t * dirA[1] * vA)

	x_traj_B, y_traj_B = [], []
	for t in range(50): 
		x_traj_B.append(xB + t * dirB[0] * vB)
		y_traj_B.append(yB + t * dirB[1] * vB)
		

	x_values, y_values = zip(*points)
	ax.scatter(x_values, y_values, color='red')

	ax.plot(x_traj_A, y_traj_A, color='blue', linestyle='-', label='Trajectoire Avion')
	ax.plot(x_traj_B, y_traj_B, color='red', linestyle='-', label='Trajectoire Hélico')

	ax.annotate('Avion', (xA, yA), textcoords="offset points", xytext=(4, -10), ha='center')
	ax.annotate('Hélico', (xB, yB), textcoords="offset points", xytext=(4, -10), ha='center')
	ax.annotate('Origine', (0, 0), textcoords="offset points", xytext=(5,5), ha='center')

	circleA = plt.Circle((xA, yA), 3.5, color='blue', fill=False, linestyle='dotted')
	circleB = plt.Circle((xB, yB), 3.5, color='blue', fill=False, linestyle='dotted')
	ax.add_patch(circleA)
	ax.add_patch(circleB)

	circle_origin = plt.Circle((0, 0), 4, color='green', fill=False, linestyle='dotted')
	ax.add_patch(circle_origin)

	ax.grid(True)
	min_x = min(x_values)
	max_x = max(x_values)
	min_y = min(y_values)
	max_y = max(y_values)

	for t in range(0, 50):
		x_traj_A_t = xA + t * dirA[0] * vA
		y_traj_A_t = yA + t * dirA[1] * vA
		if min_x - 10 <= x_traj_A_t <= max_x + 10 and min_y - 10 <= y_traj_A_t <= max_y + 10:
			ax.scatter(x_traj_A_t, y_traj_A_t, color='blue', marker='x')
			ax.text(x_traj_A_t, y_traj_A_t, f't={t}', fontsize=8, ha='right', va='bottom', color='blue')

		x_traj_B_t = xB + t * dirB[0] * vB
		y_traj_B_t = yB + t * dirB[1] * vB
		if min_x - 10 <= x_traj_B_t <= max_x + 10 and min_y - 10 <= y_traj_B_t <= max_y + 10:
			ax.scatter(x_traj_B_t, y_traj_B_t, color='red', marker='x')
			ax.text(x_traj_B_t, y_traj_B_t, f't={t}', fontsize=8, ha='right', va='bottom', color='red')
	ax.set_xlim(min_x - 10, max_x + 10)
	ax.set_ylim(min_y - 10, max_y + 10)
	ax.set_xlabel('X')
	ax.set_ylabel('Y')
	ax.set_title('Avions vroum')
	ax.set_aspect('equal')

	plt.savefig(path + "graphe.jpg", format='jpg')

	temps_entree_A, temps_sortie_A = temps_entree_sortie_rayon_5(xA, yA, vA)
	temps_entree_B, temps_sortie_B = temps_entree_sortie_rayon_5(xB, yB, vB)

def intersection_intervalles(interval1, interval2):
    debut1, fin1 = interval1
    debut2, fin2 = interval2
    if debut1 <= fin2 and debut2 <= fin1:
        return True
    return False

