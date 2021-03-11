class NetworkEvent:
    def __init__(self, net_id, name, nodes):
        self.net_id = net_id
        self.name = name
        self.nodes = nodes


class NetworkManager:

    def __init__(self):
        self.next_net_id = 1
        self.networks = []
        self.network_events = []

    def create_net(self,first_node):
        new_net = Network(self.next_net_id)
        new_net.add_node(first_node)
        self.networks.append(new_net)
        first_node.current_net = self.next_net_id
        print("network {0:d} created".format(self.next_net_id))
        self.next_net_id += 1

    def get_network_from_id(self, id):
        for net in self.networks:
            if net.id == id:
                return net
        return None

    def merge_networks(self, id1, id2):

        net1 = self.get_network_from_id(id1)
        net2 = self.get_network_from_id(id2)

        if net1 is None or net2 is None:
            print('error merging network that dosnt exist')
            return
        for n in net2.nodes:
            net1.add_node(n)
            n.current_net = id1
        self.networks.remove(net2)

    def create_connection(self,node1, node2, att=0):

        con = Connection(node1, node2, att)
        node1.connections.add(con)
        if node1.current_net is not None:
            event = NetworkEvent(node1.current_net, 'connecting node', [node1])
            self.network_events.append(event)


    def update_connection(self,node1,node2,att):
        if node1 is None or node2 is None:
            return
        #checks if connection exist
        exists = False
        old_con = None
        for con in node1.connections:
            if con.node2 is node2:
                exists = True
                old_con = con

        if exists:
            if att is not None:
                if att != old_con.att:
                    old_con.att = att
                    event = NetworkEvent(node1.current_net, 'change attenuation', [node1, node2])
                    self.network_events.append(event)
            else:
                self.remove_connection(node1,node2)
        elif not exists and att is not None:
            self.create_connection(node1,node2,att)


    def remove_connection(self, node1, node2):
        con_to_remove = []
        for con in node1.connections:
            if con.node2 == node2:
                con_to_remove.append(con)
        for con in con_to_remove:
            node1.connections.remove(con)
        if node1.current_net is not None:
            event = NetworkEvent(node1.current_net, 'removing connection', [node1])
            self.network_events.append(event)

    def build_net_from(self, node0):
        open_list = list(node0.get_connected_nodes())
        id = node0.current_net
        if id is None:
            return
        net = self.get_network_from_id(id)
        while len(open_list) > 0:
            node = open_list[0]
            if node.current_net == id:
                net.add_node(node)
            elif node.current_net is not None:
                self.merge_networks(id, node.current_net)
            else:
                net.add_node(node)
                node.current_net = id
                open_list += node.get_connected_nodes()
            open_list.remove(node)


    def update(self):
        for event in self.network_events.copy():
            net = self.get_network_from_id(event.net_id)
            if net is not None:
                if event.name == 'change attenuation':
                    pass
                if event.name == 'connecting node':
                    self.build_net_from(event.nodes[0])
                if event.name == 'removing node':
                    for n in event.nodes:
                        for c in n.connections:
                            c.connections.remove(n)
                        net.nodes.remove(n)
                    nodes_left = list(net.nodes)
                    self.networks.remove(net)
                    for n in nodes_left:
                        n.current_net = None
                        n.state = 0
                    sources = [n for n in net.nodes if n.is_source]
                    for s in sources:
                        self.create_net(s)
                        self.build_net_from(s)
                if event.name == 'removing connection':
                    nodes_left = list(net.nodes)
                    self.networks.remove(net)
                    for n in nodes_left:
                        n.current_net = None
                        n.state = 0
                    sources = [n for n in net.nodes if n.is_source]
                    for s in sources:
                        self.create_net(s)
                        self.build_net_from(s)
                net.needs_update = True

            else:
                print('received event for non existing network')

            self.network_events.remove(event)
        for net in self.networks:
            if net.needs_update:
                net.update_values()



class Network:
    def __init__(self, id):
        self.id = id
        self.nodes = set()
        self.needs_update = True

    def add_node(self, node):
        self.nodes.add(node)

    def update_values(self):

        sources = [n for n in self.nodes if n.is_source]
        updated_nodes = []
        open_con_list = []

        for s in sources:
            s.state = 16

            updated_nodes.append(s)
            open_con_list += list(s.connections)

            while len(open_con_list) > 0:
                con = open_con_list[0]
                att = con.att
                node1 = con.node1
                next_state = node1.state - att
                next_state = 0 if next_state < 0 else next_state
                node2 = con.node2
                if node2 not in updated_nodes:
                    node2.state = next_state
                    updated_nodes.append(node2)
                    if next_state > 0:
                        open_con_list += list(node2.connections)
                else:
                    if node2.state < next_state:
                        node2.state = next_state
                        open_con_list += list(node2.connections)
                open_con_list.remove(con)


            #to finish: all the nodes that havent been explored should be set at 0
            devices_to_update = []
            for n in self.nodes:
                if n not in updated_nodes:
                    n.state = 0
                else:
                    if n.device not in devices_to_update:
                        devices_to_update.append(n.device)
            #for dev in devices_to_update:
            #    dev.update()
        self.needs_update = False


class Node:
    def __init__(self, pos, device, is_source=False):
        self.pos = pos
        self.device = device
        self.is_source = is_source
        self.connections = set()
        self.state = 0
        self.current_net = None

    def initialize(self):
        print("init :", self.pos)

    def get_connected_nodes(self):
        return [con.node2 for con in self.connections]



class Connection:
    def __init__(self, node1, node2, att=0):
        self.node1 = node1
        self.node2 = node2
        self.att = att
    def get_reverse(self):
        return Connection(self.node2, self.node1, self.att)