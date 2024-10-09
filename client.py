import socket

def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('localhost', 8080))
    
    try:
        num = int(input("Enter an integer: "))
        client.send(str(num).encode('utf-8'))
        
        res = client.recv(4096).decode('utf-8')
        print(res)
    finally:
        client.close()

if __name__ == "__main__":
    start_client()
