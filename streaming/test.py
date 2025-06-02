import lambda_function

event ={
    "Records":
}

result= lambda_function.lambda_handler(event,None)
print(result)
