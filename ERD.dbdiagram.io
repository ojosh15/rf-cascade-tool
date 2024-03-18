// Use DBML to define your database structure
// Docs: https://dbml.dbdiagram.io/docs
Project rf_cascade_tool {
  database_type: 'PostgreSQL'
  Note: '''
    this DB design is for the RF Cascade Tool

    The database stores projects, which represent particular systems.
    Within a project, there are paths with inputs and outputs.
    These paths are made up of a chain of RF components.
    The component specific data can be queried and used to perform cascaded analysis.
    '''
}

Table projects {
  id integer [primary key]
  name varchar
  description varchar [null]
  created_at timestamp
}

Table paths {
  id integer [primary key]
  project_id integer
  input varchar [note: 'Typically a jack number, but could be a particular component or an antenna.']
  output varchar [note: 'Typically a jack number, but could be a particular component or an antenna.']
  description varchar [null]
}

Table components {
  id integer [primary key]
  model varchar(50)
  manufacturer varchar(50)
  type_id integer
  source source_type
  start_freq integer
  stop_freq integer
  gain json [note: 'JSON format = {Freq(Hz): value(dB)}']
  nf json [note: 'JSON format = {Freq(Hz): value(dB)}']
  p1db json [note: 'JSON format = {Freq(Hz): value(dB)}, DB will store p1db output by default']
  ip2 json [note: 'JSON format = {Freq(Hz): value(dB)}']
  ip3 json [note: 'JSON format = {Freq(Hz): value(dB)}']
  max_input json [note: 'JSON format = {Freq(Hz): value(dB)}']
  is_active bool
  is_variable bool [note: '''Some components have variable gain
  and the models will need to update dynamically/perform analyses at
  different gain settings to determine max input and P1dB etc...''']
  description varchar [null]
  version integer [default: 1, note: 'PUT/PATCH will auto-increment version and save a copy of previous version to component_versions table']
  created_at timestamp
}

Table component_versions {
  id integer [primary key]
  component_id integer
  model varchar(50)
  manufacturer varchar(50)
  type_id integer
  source source_type
  start_freq integer
  stop_freq integer
  gain json [note: 'JSON format = {Freq(Hz): value(dB)}']
  nf json [note: 'JSON format = {Freq(Hz): value(dB)}']
  p1db json [note: 'JSON format = {Freq(Hz): value(dB)}, DB will store p1db output by default']
  ip2 json [note: 'JSON format = {Freq(Hz): value(dB)}']
  ip3 json [note: 'JSON format = {Freq(Hz): value(dB)}']
  max_input json [note: 'JSON format = {Freq(Hz): value(dB)}']
  is_active bool
  is_variable bool [note: '''Some components have variable gain
  and the models will need to update dynamically/perform analyses at
  different gain settings to determine max input and P1dB etc...''']
  description varchar [null]
  version integer [default: 1, note: 'PUT/PATCH will auto-increment version and save a copy of previous version to component_versions table']
  created_at timestamp
}

Table types {
  id integer [primary key]
  type varchar(50)
}

Table path_stackup {
  path_id integer 
  component_id integer
  component_order integer [unique, not null, default: 0]
  
  indexes {
    (path_id, component_id) [pk]
  }
}

Enum source_type {
  simulated
  measured
}

Ref: paths.project_id > projects.id // many-to-one
Ref: path_stackup.path_id > paths.id
Ref: path_stackup.component_id > components.id
Ref: components.type_id > types.id
Ref: components.id < component_versions.component_id