import apps

if __name__ == "__main__":
    nett = []
    shmt = []
    dockernett = []
    dockershmt = []
    
    for i in range(10):
        nett.append(apps.net.main())
        shmt.append(apps.shm.main())
        dockernett.append(apps.dockernet.main())
        dockershmt.append(apps.dockershm.main())

    print("net", nett)
    print("shm", shmt)
    print("dockernet", dockernett)
    print("dockershm", dockershmt)
