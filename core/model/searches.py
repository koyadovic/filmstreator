from typing import List


class Condition:
    OPERATOR_EQUALS = 'eq'
    OPERATOR_NON_EQUALS = 'neq'
    OPERATOR_LESS_THAN = 'lt'
    OPERATOR_GREAT_THAN = 'gt'
    OPERATOR_LESS_OR_EQUAL_THAN = 'lte'
    OPERATOR_GREAT_OR_EQUAL_THAN = 'gte'

    ALL_OPERATORS = (OPERATOR_EQUALS, OPERATOR_NON_EQUALS, OPERATOR_LESS_THAN, OPERATOR_LESS_OR_EQUAL_THAN,
                     OPERATOR_GREAT_THAN, OPERATOR_GREAT_OR_EQUAL_THAN)

    def __init__(self, field_path, operator, value):
        assert operator in Condition.ALL_OPERATORS, 'Invalid operator provided'
        self.field_path = field_path
        self.operator = operator
        self.value = value


class Search:
    """
    (
        # this three will be AND
        (Condition, Condition, Condition),  # OR
        (Confition),  # only one condition
    )

    True if one of all conditions for whatever group of conditions is True.
    """
    def __init__(self):
        self.conditions = [[]]

    def add_condition(self, condition: Condition) -> None:
        self.conditions[-1].append(condition)

    def add_conditions(self, conditions: List[Condition]) -> None:
        self.conditions[-1] = self.conditions[-1] + conditions

    def add_or(self) -> None:
        self.conditions.append([])
