#! /usr/bin/env python3
import argparse
import json
import logging
import logging.config
import os
import sys
import time
from concurrent import futures
import ServerSideExtension_pb2 as SSE
import grpc
from src import *
import pandas as pd

_ONE_DAY_IN_SECONDS = 60 * 60 * 24

class ExtensionService(SSE.ConnectorServicer):
    """
    A simple SSE-plugin created for the Column Operations example.
    """

    def __init__(self, funcdef_file):
        """
        Class initializer.
        :param funcdef_file: a function definition JSON file
        """
        self._function_definitions = funcdef_file
        """ 
        if a "logging" directory does not exist, make it and configure logging
        """
        if not os.path.exists('logs'):
            os.mkdir('logs')
        log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logger.config')
        logging.config.fileConfig(log_file)
        logging.info('Logging enabled')

    @property
    def function_definitions(self):
        """
        :return: json file with function definitions
        """
        return self._function_definitions
    
    """
    This defines a mapping from the function IDs in the JSON Function
    definition file to the actual name of the functions that are
    implemented below
    """

    @property
    def functions(self):
        """
        :return: Mapping of function id and implementation
        """
        return {
            0: '_random_forest',
            1: '_xgboost'
        }

    """
    Implementation of added functions.
    """
    @staticmethod
    def _random_forest(request):

        df_columns = pd.read_csv("data/test.csv")
        df_final = pd.DataFrame(columns=df_columns.columns)

        for request_rows in request:

            for row in request_rows.rows:
                params = [d.strData for d in row.duals]

                result = params[0].split("|")

                df_result = pd.DataFrame(data=[result],columns=df_columns.columns)

                df_final = df_final.append(df_result, ignore_index=True)

        df_model = random_forest(df_final)
        df_model = df_model.applymap(str)

        df_model['combinado'] = df_model.apply(lambda row: '|'.join(row.values.astype(str)),axis=1)

        iter_model = df_model['combinado'].tolist()

        duals = iter([[SSE.Dual(strData=d)] for d in iter_model])

        yield SSE.BundledRows(rows=[SSE.Row(duals=d) for d in duals])

        logging.info('Funcion Ejecutada - Random Forest')

    @staticmethod
    def _xgboost(request):

        df_columns = pd.read_csv("data/test.csv")
        df_final = pd.DataFrame(columns=df_columns.columns)

        for request_rows in request:

            for row in request_rows.rows:
                params = [d.strData for d in row.duals]

                result = params[0].split("|")

                df_result = pd.DataFrame(data=[result],columns=df_columns.columns)

                df_final = df_final.append(df_result, ignore_index=True)

        df_model = xgboost(df_final)
        df_model = df_model.applymap(str)

        df_model['combinado'] = df_model.apply(lambda row: '|'.join(row.values.astype(str)),axis=1)

        iter_model = df_model['combinado'].tolist()

        duals = iter([[SSE.Dual(strData=d)] for d in iter_model])

        yield SSE.BundledRows(rows=[SSE.Row(duals=d) for d in duals])

        logging.info('Funcion Ejecutada - XGBoost')


    @staticmethod
    def _get_function_id(context):
        """
        Retrieve function id from header.
        :param context: context
        :return: function id
        """
        metadata = dict(context.invocation_metadata())
        header = SSE.FunctionRequestHeader()
        header.ParseFromString(metadata['qlik-functionrequestheader-bin'])

        return header.functionId


    """
    Implementation of rpc functions.
    """

    def GetCapabilities(self, request, context):
        """
        Get capabilities.
        Note that either request or context is used in the implementation of this method, but still added as
        parameters. The reason is that gRPC always sends both when making a function call and therefore we must include
        them to avoid error messages regarding too many parameters provided from the client.
        :param request: the request, not used in this method.
        :param context: the context, not used in this method.
        :return: the capabilities.
        """
        logging.info('GetCapabilities')

        # Create an instance of the Capabilities grpc message
        # Enable(or disable) script evaluation
        # Set values for pluginIdentifier and pluginVersion
        capabilities = SSE.Capabilities(allowScript=False,
                                        pluginIdentifier='modelos',
                                        pluginVersion='v1.0.0-beta1')

        # If user defined functions supported, add the definitions to the message
        with open(self.function_definitions) as json_file:
            # Iterate over each function definition and add data to the Capabilities grpc message
            for definition in json.load(json_file)['Functions']:
                function = capabilities.functions.add()
                function.name = definition['Name']
                function.functionId = definition['Id']
                function.functionType = definition['Type']
                function.returnType = definition['ReturnType']

                # Retrieve name and type of each parameter
                for param_name, param_type in sorted(definition['Params'].items()):
                    function.params.add(name=param_name, dataType=param_type)

                logging.info('Adding to capabilities: {}({})'.format(function.name,
                                                                     [p.name for p in function.params]))

        return capabilities

    def ExecuteFunction(self, request_iterator, context):
        """
        Call corresponding function based on function id sent in header.
        :param request_iterator: an iterable sequence of RowData.
        :param context: the context.
        :return: an iterable sequence of RowData.
        """
        # Retrieve function id
        func_id = self._get_function_id(context)
        logging.info('ExecuteFunction (functionId: {})'.format(func_id))

        return getattr(self, self.functions[func_id])(request_iterator)
 

    # """
    # Implementation of the Server connecting to gRPC.
    # """

    def Serve(self, port, pem_dir):
        """
        Server
        :param port: port to listen on.
        :param pem_dir: Directory including certificates
        :return: None
        """
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        SSE.add_ConnectorServicer_to_server(self, server)

        if pem_dir:
            # Secure connection
            with open(os.path.join(pem_dir, 'sse_server_key.pem'), 'rb') as f:
                private_key = f.read()
            with open(os.path.join(pem_dir, 'sse_server_cert.pem'), 'rb') as f:
                cert_chain = f.read()
            with open(os.path.join(pem_dir, 'root_cert.pem'), 'rb') as f:
                root_cert = f.read()
            credentials = grpc.ssl_server_credentials([(private_key, cert_chain)], root_cert, True)
            server.add_secure_port('[::]:{}'.format(port), credentials)
            logging.info('*** Running server in secure mode on port: {} ***'.format(port))
        else:
            # Insecure connection
            server.add_insecure_port('[::]:{}'.format(port))
            logging.info('*** Running server in insecure mode on port: {} ***'.format(port))

        server.start()
        try:
            while True:
                time.sleep(_ONE_DAY_IN_SECONDS)
        except KeyboardInterrupt:
            server.stop(0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', nargs='?', default='50053') # The port the plugin is run on
    parser.add_argument('--pem_dir', nargs='?') # The directory for authentification certificates
    parser.add_argument('--definition-file', nargs='?', default='FuncDefs_column.json') # The function defenition file
    args = parser.parse_args()

    # need to locate the file when script is called from outside it's location dir.
    def_file = os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), args.definition_file)

    calc = ExtensionService(def_file)
    calc.Serve(args.port, args.pem_dir)
