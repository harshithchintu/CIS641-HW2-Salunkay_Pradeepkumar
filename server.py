import socket
import threading

def prime_nums(limit):
    primes = []
    is_prime = [True] * (limit + 1)
    for p in range(2, limit + 1):
        if is_prime[p]:
            primes.append(p)
            for multiple in range(p * p, limit + 1, p):
                is_prime[multiple] = False
    return primes

def find_product(n, primes):
    for prime in primes:
        if prime >= n:
            break
        if n % prime == 0 and (n // prime) in primes:
            return prime
    return None

def handle_client(client_socket):
    try:
        data = client_socket.recv(1024).decode('utf-8')
        number = int(data)
        
        prime_candidate = find_product(number, primes)
        if prime_candidate:
            response = f"One of the primes is: {prime_candidate}"
        else:
            response = "The number is not a product of two primes."
        
        client_socket.send(response.encode('utf-8'))
    finally:
        client_socket.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', 8080))
    server.listen(5)
    print("Server listening on port 8080...")
    
    while True:
        client_socket, addr = server.accept()
        print(f"Accepted connection from {addr}")
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()

primes = prime_nums(7919)

if __name__ == "__main__":
    start_server()
