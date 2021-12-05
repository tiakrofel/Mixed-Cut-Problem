import networkx as nx
import matplotlib.pyplot as plt
import random

from networkx.algorithms.flow import minimum_cut
from networkx.algorithms.flow import maximum_flow
from networkx.algorithms.connectivity import edge_connectivity
from networkx.algorithms.connectivity.cuts import minimum_edge_cut
from networkx.algorithms.components import is_connected


def matrika_povezav(velikost=5):
    M = [[] for i in range(velikost-1)]
    for i in range(velikost-1):
        for j in range(i,velikost-1):
            M[i].append(random.randrange(2))
    return M


def matrika_v_neusmerjen_graf(matrika=None):
    graf = nx.Graph()
    if matrika == None:
        matrika = matrika_povezav()
    velikost = len(matrika)
    for i in range(velikost+1): 
        for j in range(i+1,velikost+1): 
            if matrika[i][j-i-1]:
                graf.add_edge(i+1, j+1, capacity = 1, weight=1)
    return graf


def podrobneje_graf(graf, vozlisce=None):
    vozlisca = list(graf.nodes)
    povezave = list(graf.edges)
    if vozlisce != None:
        sosedje = list(graf.neighbors(vozlisce))
    else:
        sosedje = None
    if not sosedje:
        if nx.is_directed(graf):
            return (f"Usmerjen graf, vozlisca: {vozlisca}, povezave: {povezave}")
        else:
            return (f"Neusmerjen graf, vozlisca: {vozlisca}, povezave: {povezave}")
    else:
        if nx.is_directed(graf):
            return (f"Usmerjen graf, vozlisca: {vozlisca}, povezave: {povezave}, sosedje vozlisca {vozlisce}: {sosedje}")
        else:
            return (f"Neusmerjen graf, vozlisca: {vozlisca}, povezave: {povezave}, sosedje vozlisca {vozlisce}: {sosedje}")


def obstoj_poti(G, s, t):
    try:
        sp = nx.shortest_path(G, s, t)
    except nx.NetworkXNoPath:
        return False
    return True


def povezava_med_vozliscema(graf, s, t):
    return obstoj_poti(graf, s, t)


def odstrani_vozlisce(graf, vozlisce):
    graf.remove_node(vozlisce)
    return graf


def prekini_povezavo(graf, v1, v2):
    if v1 in graf.nodes and v2 in graf.nodes and (v1, v2) in graf.edges:
        graf.remove_edge(v1, v2)
        besedilo = f"Odstranimo povezavo ({v1}, {v2})."
        if (v2, v1) in graf.edges:
            graf.remove_edge(v2, v1)
            besedilo = f"Odstranimo povezavi ({v1}, {v2}) in ({v2}, {v1})."
        return graf, besedilo
    elif v1 in graf.nodes and v2 in graf.nodes and (v2, v1) in graf.edges:
        graf.remove_edge(v2, v1)
        besedilo = f"Odstranimo povezavo ({v2}, {v1})."
        return graf,besedilo
    elif v1 not in graf.nodes:
        #Vozlisca {v1} ni v podanem grafu.
        pass
    elif v2 not in graf.nodes:
        #Vozlisca {v2} ni v podanem grafu.
        pass
    elif (v1, v2) not in graf.edges and (v2, v1) not in graf.edges:
        #Vozlisci {v1} in {v2} v podanem grafu nista povezani.
        pass
    elif v1 == v2:
        #Dvakrat je podano isto vozlisce.
        pass
    else:
        raise nx.NetworkXError(f"Prislo je do napake pri prekinjanju povezave med {v1} in {v2}.")


def razbij(graf, s, t, vozlisce, komponente):
    G = graf.copy()
    if vozlisce != None and isinstance(vozlisce, int):
        odstrani_vozlisce(G, vozlisce)
    if is_connected(G):
        print(f"Graf, ki ga sedaj razbijamo, je glede na vozlišči s in t {edge_connectivity(G,s,t)}-povezan po povezavah")
        print(f"Optimalno je, da odstranimo naslednje povezave: {minimum_edge_cut(G,s,t)}")
    if komponente != None:
        A, B = komponente
        for u in A:
            for v in B:
                if (u, v) in G.edges():
                    _, besedilo = prekini_povezavo(G, u, v)
                    print(besedilo)
    print(podrobneje_graf(G))
    print("")
    nx.draw(G, with_labels=True)
    plt.draw()
    plt.show()
    

def razbij_veckrat(graf, s, t, slovar_moznosti):
    for kljuc in slovar_moznosti:
        print(f"Odstranimo vozlisce {kljuc}")
        razbij(graf, s, t, kljuc, slovar_moznosti[kljuc])


def algoritem(podan_graf, s, t):
    graf = podan_graf.to_directed()
    print(f"Podan graf je brez odstranjenih vozlišč glede na vozlišči s in t {edge_connectivity(podan_graf,s,t)}-povezan po povezavah.")
    print("")
    if not povezava_med_vozliscema(graf, s, t):
        raise nx.NetworkXError(f"Vozlisci {s} in {t} v podanem grafu ze lezita v nepovezanih komponentah.")
    for i in graf.nodes:
        if i != s and i !=t:
            G = graf.copy()
            G.remove_node(i)
            if not povezava_med_vozliscema(G,s,t):
                print(f"Graf uspesno razbit z odstranitvijo vozlisca {i} in ohranjenimi vsemi povezavami.")
                return razbij(podan_graf, s, t, i, None)
    print("Razbitje z odstranitvijo le enega vozlisca ni mogoce.")
    print("")
    najvecji_pretok = maximum_flow(graf, s, t)[0]
    odstranjevanje_vozlisc = [0]
    for vozlisce in list(graf.nodes):
        if vozlisce != s and vozlisce != t:
            G = graf.copy()
            G.remove_node(vozlisce)
            if najvecji_pretok > maximum_flow(G, s, t)[0]:
                najvecji_pretok = maximum_flow(G, s, t)[0]
                odstranjevanje_vozlisc = [vozlisce]
            elif najvecji_pretok == maximum_flow(G, s, t)[0]:
                odstranjevanje_vozlisc.append(vozlisce)
    # sedaj vemo, katero vozlisce (ali vec moznosti zanj oziroma nobeno) se nam najbolj splaca odstraniti,
    # da za razbitje podanega grafa odstranimo najmanjse stevilo povezav
    if odstranjevanje_vozlisc == [0]:
        # izracunamo min-cut za graf brez odstranjevanja vozlisc in to je nase iskano razbitje
        stevilo, (A, B) = minimum_cut(graf, s, t)
        print(f"Graf je glede na vozlisci s in t {edge_connectivity(graf,s,t)}-povezan po povezavah,")
        print(f"torej moramo odstraniti najmanj {stevilo} povezav.")
        print("")
        return razbij(podan_graf, s, t, None, (A, B))
    elif len(odstranjevanje_vozlisc) == 1:
        # izracunamo min-cut za graf brez danega vozlisca in to je nase iskano razbitje
        odstrani_vozlisce(graf, odstranjevanje_vozlisc[0])
        stevilo, (A, B) = minimum_cut(graf, s, t)
        print(f"""Najmanjse stevilo povezav, ki jih moramo odstraniti, je {stevilo}, 
        saj je naš graf, ko odstranimo vozlisce {odstranjevanje_vozlisc[0]}, glede na vozlisci s in t
        {edge_connectivity(graf,s,t)}-povezan po povezavah.""")
        print("")
        return razbij(podan_graf, s, t, odstranjevanje_vozlisc[0], (A, B))
    elif len(odstranjevanje_vozlisc) > 1:
        # izracunamo min-cut za graf brez vsakega izmed danih vozlisc in 
        # dobimo vec moznosti za nase iskano optimalno razbitje
        moznosti = {}
        if 0 in odstranjevanje_vozlisc:
            print("Odstranjevanje vozlisc ne zmanjsa stevila povezav, ki jih moramo odstraniti za ustrezno razbitje grafa.")
            print("")
            stevilo, (A, B) = minimum_cut(graf, s, t)
            return razbij(podan_graf, s, t, None, (A,B))
        for vozlisce in odstranjevanje_vozlisc:
            G = graf.copy()
            odstrani_vozlisce(G, vozlisce)
            stevilo_v, par = minimum_cut(G, s, t)
            moznosti[vozlisce] = par
            stevilo = stevilo_v
        print(f"""Najmanjse stevilo povezav, ki jih moramo odstraniti, je {stevilo}, do tega pa lahko pridemo na vec razlicnih nacinov,
                    in sicer z odstranitvijo enega izmed vozlisc:""")
        for v in odstranjevanje_vozlisc:
            print(v)
        print("")
        return razbij_veckrat(podan_graf, s, t, moznosti)
    else:
        return("Nekaj se je zalomilo...")


# sedaj lahko bodisi podamo zeljeno stevilo vozlisc
# kot argument v funkcijo matrika_povezav() bodisi le pozenemo
# program in matrika bo avtomatsko imela 5 vrstic in 5 stolpcev:

M = matrika_povezav()

G = matrika_v_neusmerjen_graf(M)
print(podrobneje_graf(G))

s, t = random.sample(list(G.nodes), 2)
print(f"s = {s}, t = {t}")

# narišemo prvotni generiran graf
pos = nx.spring_layout(G) 
nx.draw(G, with_labels=True)
plt.draw()
plt.show()

algoritem(G, s, t)


# sproti se rezultati izpisujejo v terminal