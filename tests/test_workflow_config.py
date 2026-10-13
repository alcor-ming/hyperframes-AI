import sys
from pathlib import Path
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '.studio'))
import workflow_config as flow


class WorkflowConfigTest(unittest.TestCase):
    def test_independent_gates_and_scope(self):
        work={'series_workflow': {'human_confirmation': {'plan': False}},
              'workflow_settings': {'human_confirmation': {'draft': False}}}
        result=flow.resolve(work, {'workflow_settings': {'draft_review': {'enabled': False}}})
        self.assertEqual({'script': True, 'plan': False, 'draft': False}, result['values']['human_confirmation'])
        self.assertFalse(result['values']['draft_review']['enabled'])
        self.assertEqual('series', result['sources']['human_confirmation.plan'])
        with self.assertRaisesRegex(ValueError,'Shared Script'):
            flow.resolve(work, {'workflow_settings': {'human_confirmation': {'script': False}}})
        for invalid in ({'final': False}, {'draft_review': {'enabled': 0}}, {'human_confirmation': {'unknown': False}}):
            with self.assertRaises(ValueError): flow.resolve({'workflow_settings':invalid})
        self.assertTrue(flow.resolve({})['values']['human_confirmation']['plan'])

    def test_stage_recipe_selection_does_not_load_writing_into_plan(self):
        card={'stages':{'script':['writing.md'], 'plan':['plan.md'], 'draft':['motion.md']}}
        self.assertEqual(['plan.md'],flow.recipes(card,'plan'))
        self.assertEqual(['special.md'],flow.recipes(card,'plan',{'plan':['series.md']},{'plan':['special.md']}))
        self.assertEqual([],flow.recipes(card,'plan',{'plan':[]}))
        self.assertEqual(20,len(flow.recipes(card,'draft',explicit={'draft':[f'{i}.md' for i in range(20)]})))
        with self.assertRaises(ValueError): flow.recipes(card,'plan',{'plan':['../secret']})


if __name__=='__main__': unittest.main()
