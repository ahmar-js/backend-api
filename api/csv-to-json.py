from flask import Flask, Response
from flask_cors import CORS
import pandas as pd
import json

app = Flask(__name__)
CORS(app)  # allow all origins

@app.route('/csv-to-json', methods=['GET'])
def csv_to_json():
    try:
        # 1) Read your CSV
        df = pd.read_csv('data_for_dash.csv', low_memory=False)

        # 2) Filter to the two SKUs you care about
        df = df[df['im_sku'].isin(['3PBR-F6MB-5FT', 'BGR-F6MB-14OZ'])]

        # 3) Drop any “Unnamed:” index column
        df = df.drop(columns=[c for c in df.columns if c.startswith('Unnamed')], errors='ignore')

        # 4) Normalize the out_of_stock column (if present)
        if 'out_of_stock' in df.columns:
            df['out_of_stock'] = (
                df['out_of_stock']
                  .map({'True': 1, 'False': 0})
                  .astype(pd.Int64Dtype())   # pandas nullable integer
            )

        # 5) Convert the DataFrame into a list of dicts
        records = df.to_dict(orient='records')

        # 6) **Clean every record**: turn ANY pandas “na” into Python None
        clean = []
        for rec in records:
            for k, v in rec.items():
                if pd.isna(v):      # catches numpy.nan, pd.NA, pd.NaT, etc.
                    rec[k] = None
            clean.append(rec)

        # 7) Dump to a JSON string (now only None, never NaN) and return
        return Response(json.dumps(clean), mimetype='application/json')

    except Exception as e:
        err = {'error': str(e)}
        return Response(json.dumps(err), status=500, mimetype='application/json')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
