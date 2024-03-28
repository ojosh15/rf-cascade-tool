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
  name varchar [unique, not null]
  description varchar [null]
  created_at timestamp
  modified_at timestamp
}

Table paths {
  id integer [primary key]
  input varchar [not null, note: 'Typically a jack number, but could be a particular component or an antenna.']
  output varchar [not null, note: 'Typically a jack number, but could be a particular component or an antenna.']
  description varchar [null]
  created_at timestamp
  modified_at timestamp
}

Table components {
  id integer [primary key]
  model varchar(50)
  manufacturer varchar(50)
  serial_no varchar(50)
  type_id integer
  num_ports integer [default: 2]
  
  is_active bool
  is_variable bool [note: '''Some components have variable gain
  and the models will need to update dynamically/perform analyses at
  different gain settings to determine max input and P1dB etc...''']
  description varchar [null]
  created_at timestamp
  modified_at timestamp
}

Table component_versions {
  id integer [primary key]
  version integer [not null, default: 1]
  change_note varchar [not null, default: "Inital component"]
  is_verified bool [default: false]
  component_id integer
  component_data_id integer
}

Table component_data {
  id integer [primary key]
  data_source SourceEnum
  start_freq integer
  stop_freq integer
  gain json [note: 'JSON format = {Freq(Hz): value(dB)}']
  nf json [note: 'JSON format = {Freq(Hz): value(dB)}']
  p1db json [note: 'JSON format = {Freq(Hz): value(dB)}, DB will store p1db output by default']
  ip2 json [note: 'JSON format = {Freq(Hz): value(dB)}']
  ip3 json [note: 'JSON format = {Freq(Hz): value(dB)}']
  max_input json [note: 'JSON format = {Freq(Hz): value(dB)}']
}

Table component_types {
  id integer [primary key]
  type varchar(50) [unique, not null]
}

Table data_sheets {
  id integer [primary key]
  component_id integer
  file_name varchar
  file_path varchar
  content_type varchar
}

Table stackups {
  id integer [primary key]
  path_id integer [foreign key]
  component_version_id integer [foreign key]
  next_stackup_id integer [unique, null, foreign key]
}

Table project_paths {
  id integer [primary key]
  project_id integer [foreign key]
  path_id integer [foreign key]
} 

Enum SourceEnum {
  simulated
  measured
}

// Many-to-one/one-to-many Relationships
Ref: paths.id < project_paths.path_id
Ref: projects.id < project_paths.project_id 
Ref: stackups.path_id > paths.id 
Ref: stackups.component_version_id > component_versions.id 
Ref: components.type_id > component_types.id 
Ref: components.id < component_versions.component_id 
Ref: component_data.id < component_versions.component_data_id 
Ref: stackups.next_stackup_id > stackups.id
Ref: data_sheets.component_id > components.id