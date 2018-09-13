from collections import namedtuple
import StringIO
import networkx as nx

DEP_NODE = namedtuple('DEP_NODE', ['project', 'deployment'])


class ConfigParser(object):
    '''
        Class to parse a list of config files for their deployment
        details and dependencies
    '''

    def __init__(self, config_list):
        self.dependencies_dict = {}
        self.config_dep_dict = {}
        self.config_to_depnode_map = {}

        self.dependency_list = self.process_config_list(config_list)

    def process_config_list(self, config_list):
        '''
            Iterate through the list of `config` objects and parse the raw
            configuration for dependencies
        '''

        # Map of a deployment name to the respective config file
        config_to_depnode_map = {}
        # Dictionary of deployment dependencies
        dependencies_dict = {}
        # Dictionary of config file names dependencies
        config_dep_dict = {}

        for config in config_list:
            buf = StringIO.StringIO(config.raw)
            deployment_name, dependencies = self.find_dependencies(buf)
            dependencies_dict[deployment_name] = dependencies

            # Create the deployment to config object map
            config_to_depnode_map[deployment_name] = config

        self.dependencies_dict = dependencies_dict

        # Create dependency dictionary using the config object
        for deployment_name, dep_list in dependencies_dict.iteritems():
            config_object = config_to_depnode_map[deployment_name]
            if config_object not in config_dep_dict:
                config_dep_dict[config_object] = []

            for dep in dep_list:
                config_dep_dict[config_object].append(
                    config_to_depnode_map[dep]
                )

        self.config_dep_dict = config_dep_dict

        return config_dep_dict

    def format_deployment_name(self, project, deployment):
        """ Format the dependency to be used as an index """

        return DEP_NODE(project, deployment)

    def find_dependencies(self, buff):
        """
            Parse the configuration and get the deployment name and
            dependencies.
        """

        deployment_name = ''
        project_name = ''
        dependencies = set()
        for line in buff.readlines():
            # Ignore comments
            if '#' in line:
                continue

            # The first occurance of `name` in the file is the
            # deployment name
            if 'name:' in line and deployment_name == '':
                deployment_name = line.split()[1]

            if 'project:' in line and project_name == '':
                project_name = line.split()[1]
                deployment_name = self.format_deployment_name(
                    project_name,
                    deployment_name
                )

            # Get the deployment dependecy
            if '!DMOutput' in line:
                deployment_dep_name = line.split()
                deployment_dep_name = deployment_dep_name[2].split('/')
                deployment_dependency_project = deployment_dep_name[2]
                deployment_dep_name = deployment_dep_name[3]
                dependencies.add(
                    self.format_deployment_name(
                        deployment_dependency_project,
                        deployment_dep_name
                    )
                )

        return deployment_name, list(dependencies)

    def get_dependency_list(self):
        ''' Return the configuration dependency list '''
        return self.dependency_list


class Dependency(object):

    def __init__(self, dependency_dict):

        self.graph = nx.DiGraph()

        # Nodes with no dependents or dependencies
        self.isolates_list = []

        # List of dependencies that can be traversed sequentially
        self.sequential_dependencies_list = []

        # List of root nodes with no dependents
        self.root_list = []

        # List of nodes groups all nodes of the same dependency level
        self.level_dependencies_list = []

        # True if the a cyclical dependency is found
        self.is_cyclic = False

        for key, value in dependency_dict.iteritems():
            self.graph.add_node(key)
            for dep in value:
                self.graph.add_edge(dep, key)

        # Create the dependencies
        self.create_dependencies()


    # Create the dependency graph
    # Returns TRUE if the graph is acyclical false otherwise
    def create_dependencies(self):
        """ Builds various lists from the graph """

        # Check if the graph has cyclical dependencies
        if not nx.is_directed_acyclic_graph(self.graph):
            self.is_cyclic = True
            return False

        # List of isolated nodes (no ancestors or dependents)
        self.isolates_list = [i for i in nx.isolates(self.graph)]

        # Complete list of dependencies that can be traversed sequentially
        self.sequential_dependencies_list = [
            i for i in nx.topological_sort(self.graph)
        ]

        # List of root nodes that have dependencies (has dependents)
        for node in self.sequential_dependencies_list:
            if len(nx.ancestors(self.graph, node)) == 0:
                self.root_list.append(node)

        # Group nodes on their dependency 'levels'. Add the root nodes as the
        # first level
        self.level_dependencies_list.append(self.root_list)

        # Create a list containing a list of nodes starting from the root.
        # Each subsequent list of nodes groups all nodes of the same
        # dependency level.

        # Begin finding the successors for the root nodes
        current_list = self.root_list
        while current_list:
            level_set = set()

            # Find all the successors to the nodes and add to the set
            for node in current_list:
                successors = self.graph.successors(node)
                level_set |= set(list(successors))

            # Do not add empty sets/lists
            if level_set:
                # Add the list of nodes for this dependency level
                self.level_dependencies_list.append(list(level_set))

            # Process successors for the next level of nodes
            current_list = list(level_set)

        return True


    def get_cyclic(self):
        """ Returns true if a graph is cyclical, false otherwise """
        if self.is_cyclic:
            return nx.find_cycle(self.graph)

        return []


    def get_successors(self, node):
        """ Returns the immediate successors to `node`. """
        return [x for x in self.graph.successors(node)]


    def get_isolates(self):
        """ Returns a list of root nodes which have no dependencies """
        return self.isolates_list


    def get_roots(self):
        """ Returns a list of root nodes with dependencies """
        return self.root_list


    def get_level_dependency_list(self):
        """
            Returns a list containing a list of nodes starting from the root.
            Each subsequent list of nodes groups all nodes of the same
            dependency level. For example, the first list in the list contains
            the root nodes. The next list contains the immediate dependencies
            for the root nodes. The subsequent list contains the immediate
            dependencies for those nodes and so on and so forth.
        """
        return self.level_dependencies_list


    def get_sequential_dependency_list(self):
        """
            Returns a dictionary of the full list of dependencies.
            This list is to be traversed sequentially for all
            dependencies
         """
        return self.sequential_dependencies_list
