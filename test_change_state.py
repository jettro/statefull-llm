import unittest
from pydantic import BaseModel
from change_state import set_nested_value
from model import StateChange, LLMState


class Job(BaseModel):
    title: str = ""
    company: str = ""
    state: LLMState = LLMState()


class TestSetNestedValue(unittest.TestCase):

    def setUp(self):
        self.state = LLMState()

    def test_set_simple_value(self):
        change = StateChange(field="vacancy.title", value="Engineer", change="set")
        set_nested_value(self.state, change)
        self.assertEqual("Engineer", self.state.vacancy.title)

    def test_set_nested_value(self):
        change = StateChange(field="vacancy.wishes", value="Remote work", change="set")
        set_nested_value(self.state, change)
        self.assertIn("Remote work", self.state.vacancy.wishes)

    def test_append_to_list(self):
        change = StateChange(field="vacancy.wishes", value="Health insurance", change="append")
        set_nested_value(self.state, change)
        self.assertIn("Health insurance", self.state.vacancy.wishes)

    def test_invalid_attribute(self):
        change = StateChange(field="invalid.field", value="Test", change="set")
        with self.assertRaises(AttributeError):
            set_nested_value(self.state, change)

    def test_nested_previous_role(self):
        change = StateChange(field="experience.previous_roles",
                             value='{"title":"Software Engineer","company":"Capgemini","years":7,"description":"Worked on various projects across different domains"}',
                             change="append")
        set_nested_value(self.state, change)
        self.assertEqual("Capgemini", self.state.experience.previous_roles[0].company)

    def test_nested_previous_roles(self):
        change = StateChange(field="experience.previous_roles",
                             value='[{"title":"Software Engineer","company":"Capgemini","years":7,"description":"Worked on various projects across different domains"}]',
                             change="append")
        set_nested_value(self.state, change)
        self.assertEqual("Capgemini", self.state.experience.previous_roles[0].company)

    def test_update_nested_previous_role(self):
        change = StateChange(field="experience.previous_roles",
                             value='{"title":"Software Engineer","company":"Capgemini","years":7,"description":"Worked on various projects across different domains"}',
                             change="append")
        set_nested_value(self.state, change)
        change = StateChange(field="experience.previous_roles",
                             value='{"title":"Software Engineer","company":"Microsoft","years":2,"description":"Worked on the Windows team"}',
                             change="append")
        set_nested_value(self.state, change)
        self.assertEqual("Microsoft", self.state.experience.previous_roles[1].company)
        change = StateChange(field="experience.previous_roles[1].title", value='Search Engineer', change="set")
        set_nested_value(self.state, change)
        self.assertEqual("Search Engineer", self.state.experience.previous_roles[1].title)


if __name__ == "__main__":
    unittest.main()
