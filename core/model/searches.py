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

    search = (Search.Builder.new_search()
                            .add_condition(Condition('reference', Condition.OPERATOR_EQUALS, 'UST12345US'))
                            .add_or()
                            .add_condition(Condition('reference', Condition.OPERATOR_EQUALS, 'LALALA'))
                            .build())
    """
    def __init__(self):
        self.conditions = [[]]

    class Builder:
        def __init__(self):
            self._search = Search()

        @staticmethod
        def new_search():
            return Search.Builder()

        def add_condition(self, condition: Condition):
            self._search.conditions[-1].append(condition)

        def add_conditions(self, conditions: List[Condition]):
            self._search.conditions[-1] = self._search.conditions[-1] + conditions

        def add_or(self) -> None:
            self._search.conditions.append([])

        def build(self):
            return self._search
