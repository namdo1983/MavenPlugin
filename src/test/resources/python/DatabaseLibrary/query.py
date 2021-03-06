#  Copyright (c) 2010 Franz Allan Valencia See
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

class Query(object):
    """
    Query handles all the querying done by the Database Library. 
    """
        

    def query(self, selectStatement):
        """
        Uses the input `selectStatement` to query for the values that 
        will be returned as a list of tuples.
        
        Tip: Unless you want to log all column values of the specified rows, 
        try specifying the column names in your select statements 
        as much as possible to prevent any unnecessary surprises with schema
        changes and to easily see what your [] indexing is trying to retrieve 
        (i.e. instead of `"select * from my_table"`, try 
        `"select id, col_1, col_2 from my_table"`).
        
        For example, given we have a table `person` with the following data:
        | id | first_name  | last_name |
        |  1 | Franz Allan | See       |
        
        When you do the following:
        | @{queryResults} | Query | select * from person |
        | Log Many | @{queryResults} |
        
        You will get the following:
        [1, 'Franz Allan', 'See']
        
        Also, you can do something like this:
        | ${queryResults} | Query | select first_name, last_name from person |
        | Log | ${queryResults[0][1]}, ${queryResults[0][0]} |
        
        And get the following
        See, Franz Allan
        """
        cur = None
        try:
            cur = self._dbconnection.cursor()
            cur.execute (selectStatement);
            allRows = cur.fetchall()
            return allRows
        finally :
            if cur :
                cur.close() 

    def execute_sql_script(self, sqlScriptFileName):
        """
        Executes the content of the `sqlScriptFileName` as SQL commands. 
        Useful for setting the database to a known state before running 
        your tests, or clearing out your test data after running each a 
        test. 
        
        SQL commands are expected to be delimited by a semi-colon (';').
        
        For example:
        delete from person_employee_table;
        delete from person_table;
        delete from employee_table; 
        
        Also, the last SQL command can optionally omit its trailing semi-colon.
        
        For example:
        delete from person_employee_table;
        delete from person_table;
        delete from employee_table
        
        Given this, that means you can create spread your SQL commands in several
        lines.
        
        For example:
        delete 
          from person_employee_table;
        delete 
          from person_table;
        delete 
          from employee_table
        
        However, lines that starts with a number sign (`#`) are treated as a
        commented line. Thus, none of the contents of that line will be executed.
        
        For example:
        # Delete the bridging table first...
        delete 
          from person_employee_table;
          # ...and then the bridged tables.
        delete 
          from person_table;
        delete 
          from employee_table
        """
        sqlScriptFile = open(sqlScriptFileName)

        cur = None
        try:
            cur = self._dbconnection.cursor()        
            sqlStatement = ''
            for line in sqlScriptFile:
                line = line.strip()
                if line.startswith('#'):
                    continue
                
                sqlFragments = line.split(';')
                if len(sqlFragments) == 1:
                    sqlStatement += line + ' ';
                else:
                    for sqlFragment in sqlFragments:
                        sqlFragment = sqlFragment.strip()
                        if len(sqlFragment) == 0:
                            continue
                    
                        sqlStatement += sqlFragment + ' ';
                        
                        cur.execute(sqlStatement)
                        sqlStatement = ''

            sqlStatement = sqlStatement.strip()    
            if len(sqlStatement) != 0:
                cur.execute(sqlStatement)
                
            self._dbconnection.commit()
        except:
			self._dbconnection.rollback()
        finally:
            if cur :
                cur.close()