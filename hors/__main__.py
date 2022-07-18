import hors
from hors import process_phrase


if __name__ == '__main__':
    import cloudpickle

    cloudpickle.register_pickle_by_value(hors)
    cloudpickle.dump(process_phrase, open(f'process_phrase_v{hors.VERSION}.pkl', 'wb'))
