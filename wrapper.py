#!/usr/bin/python

import mfinder.mfinder as mfinder
import sys

##############################################################
##############################################################
# GENERAL UTILITIES
##############################################################
##############################################################

def gen_mfinder_network(links):
    links = [i for i in links if i[0] != i[1]]

    node_dict = {}
    edges = mfinder.intArray(len(links)*3)
    for i in range(len(links)):
        try:
            s,t,w = links[i]
        except ValueError:
            s,t = links[i]
            w = 1
            
        if s not in node_dict:
            node_dict[s] = len(node_dict) + 1
        if t not in node_dict:
            node_dict[t] = len(node_dict) + 1

        edges[3*i+0] = s #node_dict[s]
        edges[3*i+1] = t #node_dict[t]
        edges[3*i+2] = w

    return edges, len(links), node_dict

##############################################################
##############################################################
# MOTIF STRUCTURE CODE
##############################################################
##############################################################

def motif_structure(network,
                    motifsize = 3,
                    nrandomizations = 0,
                    usemetropolis = False,
                    ):

    # initialize the heinous input struct
    web = mfinder.mfinder_input()

    # populate the network info
    if type(network) == type("hello world"):
        web.Filename = network
    elif type(network) == type([1,2,3]):
        web.Edges, web.NumEdges, node_dict = gen_mfinder_network(network)
    else:
        sys.stderr.write("Uncle Sam frowns upon tax cheats.\n")
        sys.exit()

    # parameterize the analysis
    web.MotifSize = motifsize
    web.NRandomizations = nrandomizations
    if not usemetropolis:
        web.UseMetropolis = 0
    else:
        web.UseMetropolis = 1

    return motif_stats(web)
        
def motif_stats(mfinderi):
    results = mfinder.motif_structure(mfinderi)

    motif_stats = {}
    motif_result = results.l
    while (motif_result != None):
        motif = mfinder.get_motif_result(motif_result.p)
        motif_id = int(motif.id)
        if motif_id in motif_stats:
            sys.stderr.write("A motif has appeared twice. How odd.\n")
        else:
            motif_stats[motif_id] = dict()
            motif_stats[motif_id]['real'] = int(motif.real_count)
            motif_stats[motif_id]['rand'] = float(motif.rand_mean)
            motif_stats[motif_id]['srand'] = float(motif.rand_std_dev)
            motif_stats[motif_id]['zscore'] = float(motif.real_zscore)

        motif_result = motif_result.next

    return motif_stats

def print_motif_structure(motif_stats,sep=" ",header=False):
    if header:
        print sep.join(['motif',
                        'real',
                        'rand',
                        'srand',
                        'zscore',])

    for m in sorted(motif_stats.keys()):
        output = sep.join(["%i" % m,
                           "%i" % motif_stats[m]['real'],
                           "%.3f" % motif_stats[m]['rand'],
                           "%.3f" % motif_stats[m]['srand'],
                           "%.3f" % motif_stats[m]['zscore'],
                           ])
        print output
        #print("%i%s%i%s%.2f%s%.2f%s%.3f" % (m,
        #                                    sep,
        #                                    motif_stats[m]['real'],
        #                                    sep,
        #                                    motif_stats[m]['rand'],
        #                                    sep,
        #                                    motif_stats[m]['srand'],
        #                                    sep,
        #                                    motif_stats[m]['zscore'],
        #                                    sep
        #                                    ))
    return

##############################################################
##############################################################
# MOTIF PARTICIPATION CODE
##############################################################
##############################################################

def participation_stats(mfinderi):
    results = mfinder.motif_participation(mfinderi)

    maxed_out_member_list = False
    max_count = 0
    while True:
        maxed_out_member_list = False

        r_l = results.l
        while (r_l != None):
            motif = mfinder.get_motif(r_l.p)

            if(int(motif.count) != motif.all_members.size):
                maxed_out_member_list = True
                max_count = max(max_count, int(motif.count))

            r_l = r_l.next

        if maxed_out_member_list:
            sys.stderr.write("upping the anty bitches!\n")
            mfinderi.MaxMembersListSz = max_count + 1
            results = mfinder.motif_participation(mfinderi)

        else:
            break

    participation = {}
    r_l = results.l
    members = mfinder.intArray(mfinderi.MotifSize)
    while (r_l != None):
        motif = mfinder.get_motif(r_l.p)
        id = int(motif.id)

        am_l = motif.all_members.l
        while (am_l != None):
            mfinder.get_motif_members(am_l.p, members, mfinderi.MotifSize)
            py_members = [int(members[i]) for i in xrange(mfinderi.MotifSize)]

            for m in py_members:
                if m not in participation:
                    participation[m] = {}

                try:
                    participation[m][id] += 1
                except KeyError:
                    participation[m][id] = 1

            am_l = am_l.next

        r_l = r_l.next

    r_l = results.l
    while (r_l != None):
        motif = mfinder.get_motif(r_l.p)
        id = motif.id

        for n in participation:
            try:
                x = participation[n][id]
            except KeyError:
                participation[n][id] = 0

        r_l = r_l.next

    return participation    

def decode_participation(participation_stats,node_dictionary):
    reverse_dictionary = dict([(j,i) for i,j in node_dictionary.items()])
    return dict([(reverse_dictionary[i],j) for i,j in participation_stats.items()])

def motif_participation(network,
                        motifsize = 3,
                        maxmemberslistsz = 1000,
                        randomize = False,
                        usemetropolis = False,
                        ):

    # initialize the heinous input struct
    web = mfinder.mfinder_input()

    # populate the network info
    if type(network) == type("hello world"):
        web.Filename = network
    elif type(network) == type([1,2,3]):
        web.Edges, web.NumEdges, node_dict = gen_mfinder_network(network)
    else:
        sys.stderr.write("Uncle Sam frowns upon tax cheats.\n")
        sys.exit()

    # parameterize the analysis
    web.MotifSize = motifsize
    web.MaxMembersListSz = maxmemberslistsz

    # do we want to randomize the network first?
    if not randomize:
        web.Randomize = 0
    else:
        web.Randomize = 1
        # if so, should we use the metropolis algorithm?
        if not usemetropolis:
            web.UseMetropolis = 0
        else:
            web.UseMetropolis = 1
        
    p_stats = participation_stats(web)

    try:
        return decode_participation(p_stats,node_dict)
    except UnboundLocalError:
        return p_stats

def print_participation(participation_stats,sep=" ",header=False):
    if header:
        print sep.join(["node"]+list(map(str,sorted(participation_stats[participation_stats.keys()[0]].keys()))))

    for n in sorted(participation_stats.keys()):
        print sep.join([str(n)] + list(map(str,[j for i,j in sorted(participation_stats[n].items())])))

    return

##############################################################
##############################################################
# C'est fini
##############################################################
##############################################################