import sys
import os
import statistics as stat

cov = []
lim = []

for i in range(int(sys.argv[1]),int(sys.argv[2])):
	print("folder -> " + str(i))
	for j in range(int(sys.argv[3])):
		os.system("python3 ./analysis_tree.py " + "treeh" + str(i) + "/test_case_" + str(j) + "/test_artifact_0/ "  + str(i))
		

	metrics = {"Size": [0, 0, 0], "Height": [0, 0, 0], "Height_vs_Size": [0, 0, 0], "Leafb": [0, 0, 0], "Heightb": [0, 0, 0], "Sizeb": [0, 0, 0]}

	with open("treeh" + str(i) + "/analysis.csv", "r") as f:
		nb_X = 0
		for line in f:
			for j, v in enumerate(line[:-1].split("/")):
				tiers = v.split(";")
				for k, tier in enumerate(tiers):
					if tier == "True":
						metrics[list(metrics.keys())[j]][k] += 1

	coverage_metrics = {}
	for metric, tiers_count in metrics.items():
		cov = 0
		if(tiers_count[0] != 0):
			cov+=1
		if(tiers_count[1] != 0):
			cov+=1
		if(tiers_count[2] != 0):
			cov+=1
		coverage_metrics[metric] = str(cov) + "/3"
		
	with open("coverage.csv", "a") as f:
		f.write("\ttree h" + str(i) + "\n")
		for metric, coverage in coverage_metrics.items():
			f.write(metric + " couverture : " + coverage + "\n")







