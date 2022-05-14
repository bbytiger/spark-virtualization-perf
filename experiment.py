import apps

if __name__ == "__main__":
    nett = []
    shmt = []
    dockernett = []
    dockershmt = []
    netserializet = []
    dockernetserializet = []
    
    for i in range(10):
        nett.append(apps.net.main())
        shmt.append(apps.shm.main())
        dockernett.append(apps.dockernet.main())
        dockershmt.append(apps.dockershm.main())
        netserializet.append(apps.netserialize.main())
        dockernetserializet.append(apps.dockernetserialize.main())

    print("net", nett)
    print("shm", shmt)
    print("dockernet", dockernett)
    print("dockershm", dockershmt)
    print("netserialize", netserializet)
    print("dockernetserialize", dockernetserializet)
    
    avg = lambda x: sum(x) / len(x)

    print("""averages - net: {}, shm: {}, dockernet: {}, dockershm: {}, netserialize: {}, dockernetserialize: {}"""
            .format(avg(nett), avg(shmt), avg(dockernett), avg(dockershmt), avg(netserializet), avg(dockernetserializet)))
