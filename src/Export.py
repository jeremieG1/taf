def export(root_node, path):
	img_w = root_node.get_child_n("row").nb_instances
	img_h = img_w
	ID_field = "BM"
	# Padding is required for bitmap encoding
	padding = (4-(3*img_w)%4)%4
	
	offset = 54
	size = offset + img_w*img_h*3 + img_h*padding

	dib_header_size = 40
	nb_color_planes = 1
	bit_per_pixel = 24
	compression_method = 0
	data_size = 16
	print_resolution_w = 2835
	print_resolution_h = 2835
	nb_color = 0
	nb_important_color = 0

	with open(path + "bmp.bmp", "wb") as f:
		f.write(bytes(ID_field, 'utf-8'))
		f.write(size.to_bytes(4, 'little'))
		f.write((0).to_bytes(4, 'little'))
		f.write((54).to_bytes(4, 'little'))
		f.write(dib_header_size.to_bytes(4, 'little'))
		f.write(img_w.to_bytes(4, 'little'))
		f.write(img_h.to_bytes(4, 'little'))
		f.write(nb_color_planes.to_bytes(2, 'little'))
		f.write(bit_per_pixel.to_bytes(2, 'little'))
		f.write(compression_method.to_bytes(4, 'little'))
		f.write(data_size.to_bytes(4, 'little'))
		f.write(print_resolution_w.to_bytes(4, 'little'))
		f.write(print_resolution_h.to_bytes(4, 'little'))
		f.write(nb_color.to_bytes(4, 'little'))
		f.write(nb_important_color.to_bytes(4, 'little'))

		for i in range(img_h):
			for j in range(img_w):
				gray_value = root_node.get_child_n("row", 0).get_child_n("pixel", i).get_parameter_n("gray", j).values[0]
				for k in range(3):
					f.write((gray_value).to_bytes(1, 'little'))
			for j in range(padding):
				f.write((0).to_bytes(1, 'little'))
