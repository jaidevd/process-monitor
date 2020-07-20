import os
import gramex.ml
import gramex.cache
import pandas as pd

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


def preprocess(df):
    preprocess = modelinfo.preprocess
    features = modelinfo.features
    return (pd.get_dummies(df[features.categorical])
            .reindex(columns=preprocess.onehot, fill_value=0)
            .join(df[features.numeric])).fillna(preprocess.imputer)


def train(handler, url=None, sheet_name=None):
    if not os.path.exists(modelinfo.path) or handler.get_arg('retrain', False):
        df = gramex.cache.open(url, sheet_name=sheet_name)
        target = modelinfo.features.target
        data = preprocess(df).join(df[target])
        model = gramex.ml.Classifier(
            model_class=modelinfo.classifier,
            input=list(data.columns.drop(target)),
            output=target)
        model.train(data)
        model.trained = True
        if not os.path.exists(os.path.dirname(modelinfo.path)):
            os.makedirs(os.path.dirname(modelinfo.path))
        model.save(modelinfo.path)
        return '{"retrained": true}'
    else:
        return '{"retrained": false}'


def predict(df):
    model = gramex.ml.load(modelinfo.path)
    return model.predict(preprocess(df))
