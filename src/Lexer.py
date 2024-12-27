ARITHMETIC_OP = ["+", "-", "*", "/", "%","^"]

###############################################################################
# --- Token ----------------------------------------------------------------- #
###############################################################################
class Token:
	def __init__(self, t, v):
		self.type = t
		self.value = v

	def __repr__(self):
		return self.type + " "*(19-len(self.type)) +" -> " + self.value


###############################################################################
# --- Lexer ----------------------------------------------------------------- #
###############################################################################
class Lexer:
	def __init__(self, t):
		self._text = t
		self._pos = 0
		self._current_char = self._text[0]
		
		self._token_array = []
		self._set_token_array()

	def _move_forward(self):
		self._pos += 1
		if self._pos > len(self._text) - 1:
			self._current_char = None
		else:
			self._current_char = self._text[self._pos]

	def _extract_index(self):
		index = "["
		while self._current_char != "]":
			if self._current_char == "[":
				self._move_forward()
				index += self._extract_index()
			else:
				index += self._current_char
				self._move_forward()
		index += self._current_char
		self._move_forward()
		return index

	def _get_next_token(self):
		raise NotImplementedError

	def _set_token_array(self):
		self._token_array.append(self._get_next_token())
		while self._token_array[-1].type != "EOF":
			self._token_array.append(self._get_next_token())
	
	def get_token_array(self):
		return self._token_array
	token_array = property(get_token_array)
	
	def print_token_array(self):
		for token in self._token_array:
			print(token)


###############################################################################
# --- Expr_lexer ------------------------------------------------------------ #
###############################################################################
class Expr_lexer(Lexer):
	def __init__(self, t):
		Lexer.__init__(self, t)

	def __skip_space(self):
		while self._current_char is not None and self._current_char.isspace():
			self._move_forward()

	def __extract_word(self):
		word = ""
		while self._current_char is not None and (self._current_char.isalpha() or self._current_char.isdigit() or self._current_char in ["_"]):
			word += self._current_char
			self._move_forward()
		if self._current_char is not None and self._current_char in [".", "\\", "["]:
			if word == "z3":
				return self.__extract_z3_operator()
			else:
				return self.__extract_tree_path(word)
		if len(word) == 1:
			return Token("QUANTIFIER", word)			
		elif word in ["NOT", "OR", "AND", "IMPLIES", "DISTINCT"]:
			return Token("LOGIC_OPERATOR", "z3." + word[0] + word[1:].lower())
		elif word in ["SUP", "SUPEQ", "INF", "INFEQ", "EQ", "DIF"]:
			return Token("COMPARISON_OPERATOR", word)
		elif word.lower() == "true":
			return Token("BOOLEAN_TRUE", "True")
		elif word.lower() == "false":
			return Token("BOOLEAN_FALSE", "False")
		else:
			return Token("STRING", word)

	def __extract_z3_operator(self):
		logic_operator = ""
		if self._current_char == ".":
			self._move_forward()
		else:
			exit("ERROR Z3 LOGIC OPERATOR")
		while self._current_char.isalpha():
			logic_operator += self._current_char
			self._move_forward()
		return Token("LOGIC_OPERATOR", "z3." + logic_operator)

	def __extract_number(self):
		number = ""
		while self._current_char is not None and self._current_char.isdigit():
			number += self._current_char
			self._move_forward()
		if self._current_char == ".":
			number += self._current_char
			self._move_forward()
		while self._current_char is not None and self._current_char.isdigit():
			number += self._current_char
			self._move_forward()
		return Token("NUMBER", number)

	def __extract_tree_path(self, w=""):
		tree_path = w
		path_type="TREE_PATH"
		while self._current_char is not None and self._current_char not in ([" ", ")", ","] + ARITHMETIC_OP):
			if self._current_char == "[":
				self._move_forward()
				tree_path += self._extract_index()
			else:
				tree_path += self._current_char
				c1 = self._current_char
				self._move_forward()
				c2 = self._current_char
				if(c1==c2=="\\"):
					path_type = "TREE_MULTIPATH"
		
		return Token(path_type, tree_path)

	def _get_next_token(self):
		while self._current_char is not None:
			if self._current_char.isspace():
				self.__skip_space()

			if self._current_char.isdigit():
				return self.__extract_number()
			elif self._current_char.isalpha():
				return self.__extract_word()
			elif self._current_char == ".":
				return self.__extract_tree_path()
			elif self._current_char in ARITHMETIC_OP:
				if self._current_char =='^':
					operator = '**'
				else:
					operator = self._current_char
				self._move_forward()
				return Token("ARITHMETIC OPERATOR", operator)
			elif self._current_char == "(":
				self._move_forward()
				return Token("LPAR", "(")	
			elif self._current_char == ")":
				self._move_forward()
				return Token("RPAR", ")")
			elif self._current_char == ",":
				self._move_forward()
				return Token("COMA", ",")
			else:
				print("Lexer::_get_next_token -> invalid character \"" + self._current_char + "\"")
				raise NameError
		return Token("EOF", str(self._current_char))


###############################################################################
# --- Tree_path_lexer ------------------------------------------------------- #
###############################################################################
class Tree_path_lexer(Lexer):
	def __init__(self, t):
		Lexer.__init__(self, t)

	def __extract_dot(self):
		self._move_forward()
		if self._current_char == ".":
			self._move_forward()
			return Token("PARENT", "..")
		elif self._current_char == "\\":
			return Token("SELF", ".")
		elif self._current_char.isalpha():
			word = self.__extract_word()
			if word == "nb_instances":
				return Token("NB_INSTANCES", word)
			else:
				print("Tree_path::__extract_dot -> invalid path")
				raise NameError
		else:
			print("Tree_path::__extract_dot -> invalid path")
			raise NameError

	def __extract_word(self):
		word = ""
		while self._current_char is not None and (self._current_char.isalpha() or self._current_char.isdigit() or self._current_char == "_"):
			word += self._current_char
			self._move_forward()
		return word

	def _get_next_token(self):
		while self._current_char is not None:
			if self._current_char == ".":
				return self.__extract_dot()
			elif self._current_char == "\\":
				self._move_forward()
				if self._current_char == "\\":
					self._move_forward()
					return Token("DOUBLEBACKSLASH", "\\\\")
				else:
					return Token("BACKSLASH", "\\")
			elif self._current_char == "[":
				self._move_forward()
				return Token("INDEX", self._extract_index())
			elif self._current_char.isalpha():
				word = self.__extract_word()
				return Token("ELEMENT", word)
			else:
				t = self._current_char
				self._move_forward()
				return Token("OTHER", t)
		return Token("EOF", str(self._current_char))
