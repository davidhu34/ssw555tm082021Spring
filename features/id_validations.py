from typing import List, DefaultDict
from collections import defaultdict
from gedcom import GedcomRepository


def unique_ids(repo: GedcomRepository) -> List[str]:
  ''' US22: vaildate all individual and family ID's are unique '''
  errors: List[str] = []

  for id, individuals in repo.individual_duplicates.items():
    if len(individuals) > 1:
      line_nos_info: str = ", ".join(
          [f'{individual.line_no}' for individual in individuals])
      errors.append(
          f'ERROR US22: Individual ID ({id}) is not unique (at line {line_nos_info})')

  for id, families in repo.family_duplicates.items():
    if len(families) > 1:
      line_nos_info: str = ", ".join(
          [f'{family.line_no}' for family in families])
      errors.append(
          f'ERROR US22: Family ID ({id}) is not unique (at line {line_nos_info})')

  return errors


def corresponding_entries(repo: GedcomRepository) -> List[str]:
  ''' US26: vaildate all ID's have corresponding entries '''
  errors: List[str] = []

  for individual in repo.individuals:
    # get the line numbers and ID's for all FAMS
    spouse_of_id_list: List[str] = individual.spouse_of_id_list
    spouse_of_line_no_list: List[int] = individual.spouse_of_line_no_list
    # loop through the ID's
    for i in range(len(spouse_of_id_list)):
      family_id: str = spouse_of_id_list[i]
      line_no: int = spouse_of_line_no_list[i]
      families_of_id: List[GedcomFamily] = repo.family_duplicates[family_id]

      error_line_nos: List[str] = []

      if families_of_id:
        for family in families_of_id:
          # record line number if family doesn't exist and match
          if not family or (family.husband_id != individual.id and family.wife_id != individual.id):
            error_line_nos.append(f'at line {family.line_no}')
      else:
        error_line_nos.append('not found')

      for error_line_no in error_line_nos:
        errors.append(
            f'ERROR US26: Individual({individual.id}) is not a spouse of (at line {line_no}) the corresponding family({family_id} {error_line_no})')

  for individual in repo.individuals:
    # get the line numbers and ID's for all FAMC
    child_of_id_list: List[str] = individual.child_of_id_list
    child_of_line_no_list: List[int] = individual.child_of_line_no_list
    # loop through the ID's
    for i in range(len(child_of_id_list)):
      family_id: str = child_of_id_list[i]
      line_no: int = child_of_line_no_list[i]
      families_of_id: List[GedcomFamily] = repo.family_duplicates[family_id]

      error_line_nos: List[str] = []

      if families_of_id:
        for family in repo.family_duplicates[family_id]:
          family_line_no_info: str = f'at line {family.line_no}' if family else 'not found'
          # record line number if family doesn't exist and match
          if not family or not individual.id in family.children_id_list:
            error_line_nos.append(f'at line {family.line_no}')
      else:
        error_line_nos.append('not found')

      for error_line_no in error_line_nos:
        errors.append(
            f'ERROR US26: Individual({individual.id}) is not a child of (at line {line_no}) the corresponding family({family_id} {error_line_no})')

  for family in repo.families:
    spouses: Tuple = []
    if family.husband_id:
      if family.husbands:
        for husband in family.husbands:
          spouses.append((family.husband_id, husband, family.husband_line_no))
      else:
        spouses.append((family.husband_id, None, family.husband_line_no))

    if family.wife_id:
      if family.wifes:
        for wife in family.wifes:
          spouses.append((family.wife_id, wife, family.wife_line_no))
      else:
        spouses.append((family.wife_id, None, family.wife_line_no))

    for spouse_id, spouse, spouse_line_no in spouses:
      if not spouse or not family.id in spouse.spouse_of_id_list:
        spouse_line_no_info: str = f'at line {spouse.line_no}' if spouse else 'not found'
        errors.append(
            f'ERROR US26: Family({family.id}) spouse at line {spouse_line_no} does not correspond to individual({spouse_id} {spouse_line_no_info})')

    # get the line numbers and ID's for all CHIL
    children_id_list: List[str] = family.children_id_list
    children_line_no_list: List[str] = family.children_line_no_list
    # loop through children ID's
    for i in range(len(children_id_list)):
      child_id: str = children_id_list[i]
      child_line_no: int = children_line_no_list[i]
      individuals_of_id: List[GedcomIndividual] = repo.individual_duplicates[child_id]

      error_line_nos: List[str] = []

      if individuals_of_id:
        for child in individuals_of_id:
          # record line number if individual doesn't exist and match
          if not child or not family.id in child.child_of_id_list:
            error_line_nos.append(f'at line {child.line_no}')

      else:
        error_line_nos.append('not found')

      for error_line_no in error_line_nos:
        errors.append(
            f'ERROR US26: Family({family.id}) child at line {child_line_no} does not correspond to individual({child_id} {error_line_no})')

  return errors
