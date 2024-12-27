def export(root_node, path):
	nb_tax_payer = root_node.get_child_n("tax_payer").nb_instances
	with open(path + "tax.csv", "w") as f:
		f.write(str(nb_tax_payer) + "\n")
		for i in range(nb_tax_payer):
			f.write(str(root_node.get_child_n("tax_payer").get_parameter_n("birth_year", i).values[0]) + ";" + str(root_node.get_child_n("tax_payer").get_parameter_n("disability_rate", i).values[0]) + ";" + str(root_node.get_child_n("tax_payer").get_parameter_n("disability_type", i).values[0]) + ";" + str(root_node.get_child_n("tax_payer").get_parameter_n("is_resident", i).values[0]) + "\n")

			address = ""
			for j in range(root_node.get_child_n("tax_payer").get_child_n("address", i).nb_instances):
				address += root_node.get_child_n("tax_payer").get_child_n("address", i).get_parameter_n("country", j).values[0] + ";"
			f.write(address[:-1] + "\n")

			child = root_node.get_child_n("tax_payer").get_child_n("child", i)
			if child == None:
				f.write("0\n")
			else:
				nb_child = child.nb_instances
				f.write(str(nb_child) + "\n")
				child = ""
				for j in range(nb_child):
					child += str(root_node.get_child_n("tax_payer").get_child_n("child", i).get_parameter_n("birth_year", j).values[0]) + ";" + str(root_node.get_child_n("tax_payer").get_child_n("child", i).get_parameter_n("disability_rate", j).values[0]) + ";" + str(root_node.get_child_n("tax_payer").get_child_n("child", i).get_parameter_n("disability_type", j).values[0]) + "\n"
					nb_child_address = root_node.get_child_n("tax_payer").get_child_n("child", i).get_child_n("address", j).nb_instances
					for k in range(nb_child_address):
						child += str(root_node.get_child_n("tax_payer").get_child_n("child", i).get_child_n("address", j).get_parameter_n("country", k).values[0]) + ";"
					child = child[:-1] + "\n"
				f.write(child)

			income_pension = root_node.get_child_n("tax_payer").get_child_n("income_pension", i)
			if income_pension == None:
				f.write("0\n")
			else:
				nb_income_pension = income_pension.nb_instances
				f.write(str(nb_income_pension) + "\n")
				income_pension = ""
				for j in range(nb_income_pension):
					income_pension += str(root_node.get_child_n("tax_payer").get_child_n("income_pension", i).get_parameter_n("is_local", j).values[0]) + ";"
				f.write(income_pension[:-1] + "\n")

			income_employment = root_node.get_child_n("tax_payer").get_child_n("income_employment", i)
			if income_employment == None:
				f.write("0\n")
			else:
				nb_income_employment = income_employment.nb_instances
				f.write(str(nb_income_employment) + "\n")
				income_employment = ""
				for j in range(nb_income_employment):
					income_employment += str(root_node.get_child_n("tax_payer").get_child_n("income_employment", i).get_parameter_n("is_local", j).values[0]) + ";"
				f.write(income_employment[:-1] + "\n")
			
			income_other = root_node.get_child_n("tax_payer").get_child_n("income_other", i)
			if income_other == None:
				f.write("0\n")
			else:
				nb_income_other = income_other.nb_instances
				f.write(str(nb_income_other) + "\n")
				income_other = ""
				for j in range(nb_income_other):
					income_other += str(root_node.get_child_n("tax_payer").get_child_n("income_other", i).get_parameter_n("is_local", j).values[0]) + ";"
				f.write(income_other[:-1] + "\n")

