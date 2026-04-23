from flask import Flask, request, jsonify

app = Flask(__name__)

products = [
    {
        "id": 1,
        "name": "Computadora HP Probook 450 G10",
        "price": 100,
        "description": "Computadora HP Probook 450 G10 con procesador Intel Core i5-1135G7, 8GB de RAM y 256GB de SSD",
        "image": "https://www.hp.com/us-en/shop/app/assets/images/uploads/prod/hp-probook-450-g10-24-3x2-2-01.png"
    },
    {
        "id": 2,
        "name": "Computadora HP Probook 450 G10",
        "price": 100,
        "description": "Computadora HP Probook 450 G10 con procesador Intel Core i5-1135G7, 8GB de RAM y 256GB de SSD",
        "image": "https://www.hp.com/us-en/shop/app/assets/images/uploads/prod/hp-probook-450-g10-24-3x2-2-01.png"
    },
    {
        "id": 3,
        "name": "Computadora HP Probook 450 G10",
        "price": 100,
        "description": "Computadora HP Probook 450 G10 con procesador Intel Core i5-1135G7, 8GB de RAM y 256GB de SSD",
        "image": "https://www.hp.com/us-en/shop/app/assets/images/uploads/prod/hp-probook-450-g10-24-3x2-2-01.png"
    }
]

@app.route('/api/products')
def get_products():
    return jsonify(products)

if __name__ == '__main__':
    app.run(debug=True)