def execute_wizard_cli(self, wizard_model, input_cmd):
    # Execute wizard to input command list
    wizard = self.wizard_model.create({
        'input_cmd': input_cmd
    })
    result = wizard.execute_input()
    return result
