import gramex.ml
import gramex.cache
from gramex.config import variables
from tornado.template import Template

modelinfo = gramex.cache.open('model.yaml', 'config', rel=True)


def argparse(handler):
    return handler.argparse(
        speed={'type': int, 'default': ''},
        reactor={'type': int, 'default': 100},
        crystallizer={'type': int, 'default': 100},
        dryer={'type': int, 'default': 100},
        solvent={'type': str, 'default': ''})


def classify(data, handler):
    is_simulate = handler.path_args[0] == 'datasimulate'
    is_predict = any(k in handler.args for k in ['reactor', 'crystallizer', 'dryer', 'solvent'])
    summary = [
        'Material A', 'Material B', 'Catalyzer Type', 'Solvent Amt', 'Dryer Cycle Time (min)',
        'Dryer Speed', 'Crushing time (min)', 'Reaction Time (min)', 'Batch Number']
    df = data['batch'].assign(**data['summary'][summary].iloc[0])
    if is_simulate:
        df = simulate(df, handler)
    df = df.join(df.expanding().mean().round(1).add_prefix('Avg '))
    if (is_simulate and is_predict):
        df['Outcome'] = predict(df)
    df['isGood'] = df['Outcome'].eq('Good').astype(int)
    return df


def simulate(df, handler):
    q = argparse(handler)
    adjust = [
        ('reactor', 'Reactor Temperature'),
        ('crystallizer', 'Crystallizer Cooling Rate'),
        ('dryer', 'Dryer Temperature')]
    for param, col in adjust:
        df[col] = (df[col] * q[param] / 100).round(1)
    if q.solvent:
        df['Solvent Amt'] = q.solvent
    return df


def predict(df):
    model = gramex.ml.load(modelinfo.path)
    return model.predict(df)


def narrative(handler):
    prev_args = [k for k in handler.args if k.startswith('prev_')]
    if not prev_args:
        return f"This batch is {handler.get_argument('Outcome')}"
    found = False
    for arg in prev_args:
        previous = handler.get_argument(arg)
        current = handler.get_argument(arg.replace('prev_', ''))
        if previous != current:
            arg = arg.replace('prev_', '')
            found = True
            break
    if not found:
        return f"This batch is {handler.get_argument('Outcome')}"
    prev_outcome = handler.get_argument('prev_Outcome')
    curr_outcome = handler.get_argument('Outcome')
    verb = 'does not affect'
    if (prev_outcome, curr_outcome) == ('Bad', 'Good'):
        verb = 'improves'
    elif (prev_outcome, curr_outcome) == ('Good', 'Bad'):
        verb = 'spoils'
    return Template(variables['narrative']).generate(
        arg=arg, previous=previous, current=current, outcome_verb=verb)
