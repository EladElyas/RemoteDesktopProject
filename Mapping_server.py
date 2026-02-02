import socket

def setup_server(controlled_pcs, admin_sockets):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("10.100.102.18", 10000))
    while True:
        server.listen(5)
        cs, addr = server.accept()
        mac = cs.recv(12).decode()
        role = cs.recv(3)
        if role == b"cln":
            if mac not in controlled_pcs and mac not in admin_sockets:
                controlled_pcs[mac] = [None,None,None,None,None]
            validate_id(mac, controlled_pcs, cs)
        elif role == b"adm":
            if len(admin_sockets) < 1:
                admin_sockets[mac] = [None,None,None,None,None]
            elif mac not in admin_sockets:
                cs.close()
                #refuse additional admin connections
            validate_id(mac, admin_sockets, cs)
            


def validate_id(mac, sockets, cs):
    while True:
        try:
            data = cs.recv(1).decode().strip()
            if not data: 
                break
                
            job_id = int(data)
            if 0 <= job_id <= 4:
                sockets[mac][job_id] = cs
                cs.send(b"Yes")
                break
            else:
                cs.send(b"No")
        except (ValueError, IndexError):
            cs.send(b"No")
        
            
        
           