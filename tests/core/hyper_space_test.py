# -*- coding:utf-8 -*-
"""

"""
from hypernets.core.ops import Identity, HyperInput, DynamicModule
from hypernets.core.search_space import *


class Test_HyperSpace():
    def get_space(self):
        space = HyperSpace()
        with space.as_default():
            input1 = HyperInput()
            input2 = HyperInput()

            id1 = Identity(p1=Choice([1, 2]), p2=Int(1, 100))
            id2 = Identity(p3=Real(0, 1))
            id3 = Identity(p4=Dynamic(lambda args: args['p5'] * 3, p5=Choice([2, 4, 8])))
            id4 = Identity()
            id5 = Identity()
            id6 = Identity()
            id7 = Identity()

            id1([input1, id7])
            id2([input1, input2])
            id3([input2, id1, id2])
            id4([input1, id2])
            id5(input2)
            id6(id3)
            id7([id4, id5])
        return space

    def get_space_with_dynamic(self):

        space = HyperSpace()
        with space.as_default():
            input1 = HyperInput()
            input2 = HyperInput()

            id1 = Identity(p1=Choice([1, 2]), p2=Int(1, 100))
            id2 = Identity(p3=Real(0, 1))
            id3 = Identity(p4=Dynamic(lambda args: args['p5'] * 3, p5=Choice([2, 4, 8])))

            def new_module(m):
                dm1 = Identity(dp1=Choice(['a', 'b']))
                return dm1, dm1

            id4 = DynamicModule(dynamic_fn=new_module, p6=Choice(['f', 'g']))
            id5 = Identity()
            id6 = Identity()
            id7 = Identity()

            id1([input1, id7])
            id2([input1, input2])
            id3([input2, id1, id2])
            id4([input1, id2])
            id5(input2)
            id6(id3)
            id7([id4, id5])
        return space

    def test_basic_ops(self):
        with HyperSpace().as_default() as space:
            id1 = HyperInput()
            id2 = HyperInput()
            id3 = Identity()
            id3([id1, id2])
            id4 = Identity()
            id4(id3)
            id5 = Identity()
            id5(id3)

            graph_inputs = space.get_inputs()
            id3_inputs = space.get_inputs(id3)
            id4_inputs = space.get_inputs(id4)

            assert graph_inputs == [id1, id2]
            assert id3_inputs == [id1, id2]
            assert id4_inputs == [id3]

            graph_outputs = space.get_outputs()
            id1_outputs = space.get_outputs(id1)
            id3_outputs = space.get_outputs(id3)

            assert graph_outputs == [id4, id5]
            assert id1_outputs == [id3]
            assert id3_outputs == [id4, id5]

            space.disconnect(id3, id5)
            id3_outputs = space.get_outputs(id3)
            assert id3_outputs == [id4]

            assert len(space.modules) == 5
            assert len(space.edges) == 3

    def test_traverse(self):
        id_list = []

        def print_module(m):
            print(m.id)
            id_list.append(m.id)
            return True

        space = self.get_space()
        space.traverse(print_module, direction='forward')
        assert id_list == ['Module_HyperInput_1', 'Module_HyperInput_2', 'Module_Identity_2', 'Module_Identity_4',
                           'Module_Identity_5', 'Module_Identity_7', 'Module_Identity_1', 'Module_Identity_3',
                           'Module_Identity_6']

        id_list = []
        space.traverse(print_module, direction='backward')
        assert id_list == ['Module_Identity_6', 'Module_Identity_3', 'Module_Identity_1', 'Module_Identity_7',
                           'Module_Identity_4', 'Module_Identity_5', 'Module_Identity_2',
                           'Module_HyperInput_2', 'Module_HyperInput_1', ]

        space = self.get_space_with_dynamic()
        id_list = []
        space.traverse(print_module, direction='forward')
        assert id_list == ['Module_HyperInput_1', 'Module_HyperInput_2', 'Module_Identity_2', 'Module_Identity_4',
                           'Module_DynamicModule_1', 'Module_Identity_6', 'Module_Identity_1', 'Module_Identity_3',
                           'Module_Identity_5']

        space.Param_Choice_3.random_sample()
        id_list = []
        space.traverse(print_module, direction='forward')
        assert id_list == ['Module_HyperInput_1', 'Module_HyperInput_2', 'Module_Identity_2',
                           'Module_Identity_7', 'Module_Identity_4', 'Module_Identity_6', 'Module_Identity_1',
                           'Module_Identity_3', 'Module_Identity_5']

    def test_all_assigned(self):
        space = self.get_space()

        assert space.all_assigned == False
        space.Param_Choice_1.random_sample()
        assert space.all_assigned == False
        space.Param_Int_1.random_sample()
        assert space.all_assigned == False
        space.Param_Real_1.assign(0.1)
        assert space.all_assigned == False
        space.Param_Choice_2.random_sample()
        assert space.all_assigned == True

    def test_get_assignable_params(self):
        space = self.get_space()
        with space.as_default():
            const = Constant(1)
        assert const in space.hyper_params
        ps = space.get_assignable_params()
        assert ps == [space.Param_Real_1, space.Param_Choice_1, space.Param_Int_1, space.Param_Choice_2]

    def test_unassigned_iterator(self):
        space = self.get_space()
        ps = []
        for p in space.unassigned_iterator:
            ps.append(p)
        assert ps == [space.Param_Real_1, space.Param_Choice_1, space.Param_Int_1, space.Param_Choice_2]
        space.Param_Choice_1.random_sample()

        ps = []
        for p in space.unassigned_iterator:
            ps.append(p)
        assert ps == [space.Param_Real_1, space.Param_Int_1, space.Param_Choice_2]

        space = self.get_space_with_dynamic()
        ps = []
        for p in space.unassigned_iterator:
            ps.append(p)
        assert ps == [space.Param_Real_1, space.Param_Choice_3, space.Param_Choice_1, space.Param_Int_1,
                      space.Param_Choice_2]

        space.Param_Choice_3.random_sample()
        ps = []
        for p in space.unassigned_iterator:
            ps.append(p)
        assert ps == [space.Param_Real_1, space.Param_Choice_4, space.Param_Choice_1, space.Param_Int_1,
                      space.Param_Choice_2]

    def test_random_sample(self):
        space = self.get_space_with_dynamic()
        ps = []
        space.random_sample()
        for p in space.unassigned_iterator:
            ps.append(p)
        assert ps == []

    def test_default(self):
        dg1 = get_default_space()
        g = HyperSpace()
        with g.as_default():
            dg2 = get_default_space()
            assert dg2 == g
            assert dg2 != dg1

            with HyperSpace().as_default() as g2:
                dg3 = get_default_space()
                assert dg3 == g2
                assert dg3 != dg2

            dg4 = get_default_space()
            assert dg4 == dg2

        dg5 = get_default_space()
        assert dg5 == dg1