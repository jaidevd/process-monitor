import gramex.ml
import gramex.cache

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
