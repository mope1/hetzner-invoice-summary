from os import listdir, path
import csv
import sys

summary_csv_writer = csv.writer(sys.stdout)
summary_csv_writer.writerow(['month', 'type', 'name', 'amount', 'cost'])

invoices_path='./invoices-csv'
invoice_files = listdir(invoices_path)
invoice_files.sort() 
for filename in invoice_files:
  with open(path.join(invoices_path, filename), 'r') as csvfile:
    csv_text = csvfile.read()
    month = None

    servers={}
    snapshots={}
    block_storages={}
    floating_ips = { 'count': 0, 'cost': 0 }

    # python3 stdlib csv package does not handle newlines in column
    # doing the parsing manually
    # HACK assuming last column is empty string
    for row in csv_text.split(',""\n'):
      # HACK assuming columns are all strings
      columns = row.split('","')
      columns[1] = columns[1].split('\n') # split by newline in-place
      #print(columns)

      if month is None:
        month = columns[2][:-3]

      if 'Server' in columns[0]:
        hostname = columns[1][0].split('""')[1]
        usage_hours = float(columns[4])
        cost=float(columns[5])
        
        if hostname not in servers:
          servers[hostname] = {
            'usage_hours': usage_hours,
            'cost': cost,
          }
        else:
          servers[hostname]['usage_hours']+=usage_hours
          servers[hostname]['cost']+=cost

      elif 'Snapshot' in columns[0]:
        snapname = columns[1][0].split('""')[1]
        usage_gbs = float(columns[4])
        cost=float(columns[5])
        
        if snapname not in snapshots:
          snapshots[snapname] = {
            'usage_gbs': usage_gbs,
            'cost': cost,
          }
        else:
          snapshots[snapname]['usage_gb']+=usage_gb
          snapshots[snapname]['cost']+=cost

      elif 'Block storage' in columns[0]:

        storage_name = columns[1][0].split('""')[1]
        gb_months = float(columns[4])
        cost=float(columns[5])
        
        if storage_name not in block_storages:
          block_storages[storage_name] = {
            'gb_months': gb_months,
            'cost': cost,
          }
        else:
          block_storages[storage_name]['gb_months']+=gb_months
          block_storages[storage_name]['cost']+=cost

      elif 'Floating IP' in columns[0]:
        count = float(columns[4])
        cost=float(columns[5])
        floating_ips['count']+=count
        floating_ips['cost']+=cost

      else:
        print('Unhandled entry: '+columns)
    
    for hostname, summary in servers.items():
      summary_csv_writer.writerow([month, 'server', hostname, summary['usage_hours'], summary['cost'] ])

    for snapname, summary in snapshots.items():
      summary_csv_writer.writerow([month, 'snapshot', snapname, summary['usage_gbs'], summary['cost'] ])

    for snapname, summary in block_storages.items():
      summary_csv_writer.writerow([month, 'block_storage', snapname, summary['gb_months'], summary['cost'] ])

    if floating_ips['count'] > 0:
      summary_csv_writer.writerow([month, 'floating_ips', 'all', floating_ips['count'], floating_ips['cost'] ])