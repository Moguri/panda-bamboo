from direct.showbase.DirectObject import DirectObject


class InputMapper(DirectObject):
    def __init__(self, config, verbose=False, remap_keys=True):
        self.verbose = verbose
        self.remap_keys = remap_keys

        # Setup input map
        self.input_map = {}
        with open(config) as f:
            for ln in f.readlines():
                ln = ln.strip()
                if ln and not ln.startswith(';'):
                    ln = ln.split('=')
                    triggers = [i.strip() for i in ln[1].strip().split(',')]
                    event = ln[0].strip()

                    for trigger in triggers:
                        if self.remap_keys:
                            remapped = str(base.win.get_keyboard_map().get_mapped_button(trigger))
                            if remapped != 'none':
                                trigger = remapped

                        if trigger in self.input_map:
                            self.input_map[trigger].append(event)
                        else:
                            self.input_map[trigger] = [event]

        if self.verbose:
            import pprint
            print('Loaded input map')
            pprint.pprint(self.input_map)

        # Listen for events
        for trigger, events in self.input_map.items():
            self.accept(trigger, self.send, [events, ''])
            self.accept(trigger + '-up', self.send, [events, '-up'])
            self.accept(trigger + '-repeat', self.send, [events, '-repeat'])

    def send(self, events, suffix):
        for i in events:
            if self.verbose:
                print('InputMapper sending:', i + suffix)
            messenger.send(i + suffix)

    def get_mapped_trigger_labels(self, event):
        triggers = [key for key,value in self.input_map.items() if event in value]

        retval = []
        keymap = base.win.get_keyboard_map()
        for trigger in triggers:
            label = keymap.get_mapped_button_label(trigger)
            if not label:
                label = trigger
            retval.append(label)

        return retval
