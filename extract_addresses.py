

(number, street) = address.split(' ',1)
        f_houses.write(street + "," + number + "," +  str(np.random.uniform()<0.8) + "\n")
        
                
        contributor = np.random.uniform()<0.8
        
        if contributor:
            result += list("contributor: true,\n")
        else:
            result += list("contributor: false,\n")        