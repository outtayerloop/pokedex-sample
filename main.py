from typing import Union
import requests 
import pandas as pd
from bs4 import BeautifulSoup, PageElement, ResultSet


class TextUtil:
	"""
	Utilitary class destined to string related operations.
	"""

	@staticmethod
	def is_digit(s: str) -> bool:
		"""Determine whether the provided string is
		a number or not.

		Args:
			s (str): provided string

		Returns:
			bool: True if the string is a number (can be signed),
			otherwise returns False.
		"""
		return s[:2] != '+-'\
			and s[:2] != '-+'\
			and s.lstrip('-')\
				 .lstrip('+')\
				 .isdigit()


def get_cell_text(cell: PageElement) -> Union[str, int]:
	"""Return the current Pokedex row cell content.

	Args:
		cell (PageElement): cell from the Pokedex table

	Returns:
		Union[str, int]: Either int if the current value is numerical
		or str with leading and trailing white-spaces removed
	"""
	cell_text = cell.get_text()
	return int(cell_text)\
				if TextUtil.is_digit(cell_text)\
				else cell_text.strip()


class Pokedex:
	"""
	Represents the Pokedex table and its related operations.
	"""

	def __init__(self):
		"""
		Initialize the Pokedex table from the internal URL.
		"""
		self.__pokedex_url__ = 'http://pokemondb.net/pokedex/all'
		self.__pokedex_table__ = self.__init_table__()

	def __init_table__(self) -> PageElement:
		"""Initialize the Pokedex table page element.

		Returns:
			PageElement: Pokedex table navigational
			information
		""" 
		page = requests.get(self.__pokedex_url__) 
		soup = BeautifulSoup(page.content, 'lxml')
		return soup.find(id='pokedex')

	def get_pokedex_table(self) -> PageElement:
		"""Return the pokedex table page element.

		Returns:
			PageElement: Pokedex table navigational
			information
		"""
		return self.__pokedex_table__

	def get_pokedex_column_labels(self) -> list[str]:
		"""Return the pokedex table's column labels.

		Returns:
			list[str]: a list containing the column names
		"""
		return self.__pokedex_table__.find('thead')\
								   .get_text(separator='\n', strip=True)\
								   .split('\n')

	def get_pokedex_content_rows(self) -> ResultSet:
		"""
		Return the pokedex table content rows 
		(excluding its headers).

		Returns:
			ResultSet: a list containing all HTML <tr>
			elements inside the pokedex table except its
			columns headers. This list also keeps track of 
			the SoupTrainer that created it
		"""
		return self.__pokedex_table__.find('tbody')\
								   .find_all('tr')

	def get_pokedex_data_dict(self, column_labels: list[str], content_rows: ResultSet) -> dict[str, list[Union[str, int]]]:
		"""
		Return a dictionary built from the Pokedex content rows
		(without headers).

		Args:
			column_labels (list[str]): Pokedex headers labels
			content_rows (ResultSet): Pokedex content rows (excluding its headers)

		Returns:
			dict[str, list[Union[str, int]]]: the dictionary
			representation of the Pokedex table
		"""
		data_dict = dict.fromkeys(column_labels, [])
		for data_row in content_rows:
			row_cells = data_row.find_all('td')
			cell_col_zip = zip(row_cells, column_labels)
			for cell, col_label in cell_col_zip:
				cell_text = get_cell_text(cell)
				updated_values = data_dict[col_label] + [cell_text]
				data_dict[col_label] = updated_values
		return data_dict


if __name__ == '__main__':
	pokedex = Pokedex()
	column_labels = pokedex.get_pokedex_column_labels()
	content_rows = pokedex.get_pokedex_content_rows()
	data_dict = pokedex.get_pokedex_data_dict(column_labels, content_rows)
	df = pd.DataFrame(data_dict)
	df.to_csv('pokedex.csv', index=False)