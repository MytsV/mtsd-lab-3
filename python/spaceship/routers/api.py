from fastapi import APIRouter

router = APIRouter()


@router.get('')
def hello_world() -> dict:
    return {'msg': 'Hello, World!'}

@router.get('/product')
def matrix_product() -> dict:
    import numpy as np

    # Create two 10x10 random matrices
    matrix_a = np.random.rand(10, 10)
    matrix_b = np.random.rand(10, 10)

    # Multiply the matrices together
    result = np.dot(matrix_a, matrix_b)

    return {
        'matrix_a': matrix_a.tolist(), 
        'matrix_b': matrix_b.tolist(), 
        'product': result.tolist()
    }
