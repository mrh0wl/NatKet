

class String(str):
    @property
    def split_camelcase(self):
        start_idx = [i for i, e in enumerate(self) if e.isupper()] + [len(self)]

        start_idx = [0] + start_idx
        return ' '.join([self[x:y] for x, y in zip(start_idx, start_idx[1:])]).strip()
