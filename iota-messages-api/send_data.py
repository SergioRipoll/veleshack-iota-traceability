import json, codecs, requests
from flask import Flask, jsonify, request

app = Flask(__name__)
app.debug = True

@app.route('/upload', methods=['POST'])
def post_clear():
    node_param = request.args.get("node", "localhost")
    if not node_param.startswith("http"):
        node = f"http://{node_param}:14265/api/core/v2/blocks"
    else:
        node = f"{node_param}/api/core/v2/blocks"

    requestData = request.get_json()
    tag = requestData.get("tag", "default")
    message = json.dumps(requestData.get("message", {}))

    tag_hex = "0x" + codecs.encode(tag, 'utf-8').hex()
    message_hex = "0x" + codecs.encode(message, 'utf-8').hex()

    payload = json.dumps({
        "protocolVersion": 2,
        "payload": {
            "type": 5,
            "tag": tag_hex,
            "data": message_hex
        }
    })
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    try:
        response = requests.request("POST", node, headers=headers, data=payload)
    except Exception as e:
        return "Hornet node not found, check that the Hornet node exists.\n", 400

    block_id = None
    try:
        res_json = response.json()
        block_id = res_json.get("blockId")
    except Exception:
        pass

    # Notificación automática a la Traceability API (puerto 6000)
    if block_id:
        try:
            requests.post("http://localhost:5050/trace", json={
                "block_id": block_id,
                "tag": tag,
                "message": requestData.get("message")
            })
        except Exception as e:
            print("Error al notificar a trazabilidad:", e)

    return jsonify(
        status_code=response.status_code,
        return_payload=response.text
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5555)
