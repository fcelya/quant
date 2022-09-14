## LIBRARIES 
from statsmodels.tsa.vector_ar.vecm import coint_johansen # hay que instalarla con pip install statsmodels


## Johansen Test pasándole los datos bonitos
# la función de johansen test en la que le pasamos un raw df y lo limpia solo la haremos una vez
# entendamos como funciona bien la función básica
def johansen_test(y, p):
       
    jres = coint_johansen(y, 0, p)

    return jres
