from typing import List


class Condition:
    OPERATOR_EQUALS = 'eq'
    OPERATOR_NON_EQUALS = 'neq'
    OPERATOR_LESS_THAN = 'lt'
    OPERATOR_GREAT_THAN = 'gt'
    OPERATOR_LESS_OR_EQUAL_THAN = 'lte'
    OPERATOR_GREAT_OR_EQUAL_THAN = 'gte'
    OPERATOR_IN = 'in'
    OPERATOR_NOT_IN = 'nin'

    ALL_OPERATORS = (OPERATOR_EQUALS, OPERATOR_NON_EQUALS, OPERATOR_LESS_THAN, OPERATOR_LESS_OR_EQUAL_THAN,
                     OPERATOR_GREAT_THAN, OPERATOR_GREAT_OR_EQUAL_THAN, OPERATOR_IN, OPERATOR_NOT_IN)

    def __init__(self, field_path, operator, value):
        assert operator in Condition.ALL_OPERATORS, 'Invalid operator provided'
        self.field_path = field_path
        self.operator = operator
        self.value = value


class Search:
    target_class = None  # AudiovisualRecord, Person, Genre

    """
    (
        # this three will be AND
        (Condition, Condition, Condition),  # OR
        (Confition),  # only one condition
    )

    True if one of all conditions for whatever group of conditions is True.

    search = (Search.Builder.new_search(AudiovisualRecord)
                            .add_condition(Condition('reference', Condition.OPERATOR_EQUALS, 'UST12345US'))
                            .add_or()
                            .add_condition(Condition('reference', Condition.OPERATOR_EQUALS, 'LALALA'))
                            .build())
    """
    def __init__(self, klass):
        self.conditions = [[]]
        self.target_class = klass

    class Builder:
        def __init__(self, klass):
            self._search = Search(klass)

        @staticmethod
        def new_search(klass):
            return Search.Builder(klass)

        def add_condition(self, condition: Condition):
            self._search.conditions[-1].append(condition)
            return self

        def add_conditions(self, conditions: List[Condition]):
            self._search.conditions[-1] = self._search.conditions[-1] + conditions
            return self

        def add_or(self):
            self._search.conditions.append([])
            return self

        def search(self):
            from core import services
            return services.search(self._search)
