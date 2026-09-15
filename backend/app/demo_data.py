DEMO_REPORTS = [
 {"id":"FIR-2025-041","date":"2025-03-04","title":"Warehouse burglary report","text":"Witness saw Rohan Mehta near Eastern Freight Warehouse. Phone 9876543210 contacted Vikram Shah. A white Swift DL8CAB1234 left Sector 18, Noida.","source":"Synthetic FIR"},
 {"id":"INT-2025-088","date":"2025-03-11","title":"Financial intelligence note","text":"Account 001234567890 received repeated transfers connected to Orion Logistics. Ayesha Khan met Rohan Mehta at Cafe Meridian, Noida.","source":"Synthetic intelligence note"},
 {"id":"FIR-2025-063","date":"2025-03-19","title":"Vehicle sighting","text":"Vikram Shah used phone 9876543210 and vehicle DL8CAB1234 near Eastern Freight Warehouse. Officers noted a planned meeting on 2025-03-22.","source":"Synthetic FIR"}
]

DEMO_NODES = [
 {"id":"person:rohan-mehta","label":"Rohan Mehta","type":"Person","risk":72}, {"id":"person:vikram-shah","label":"Vikram Shah","type":"Person","risk":84},
 {"id":"person:ayesha-khan","label":"Ayesha Khan","type":"Person","risk":38}, {"id":"phone:9876543210","label":"9876543210","type":"Phone","risk":65},
 {"id":"vehicle:dl8cab1234","label":"DL8CAB1234","type":"Vehicle","risk":58}, {"id":"location:eastern-freight-warehouse","label":"Eastern Freight Warehouse","type":"Location","risk":55},
 {"id":"location:sector-18-noida","label":"Sector 18, Noida","type":"Location","risk":25}, {"id":"location:cafe-meridian-noida","label":"Cafe Meridian, Noida","type":"Location","risk":20},
 {"id":"account:001234567890","label":"001234567890","type":"Account","risk":77}, {"id":"organization:orion-logistics","label":"Orion Logistics","type":"Organization","risk":69}
]
DEMO_EDGES = [
 ("person:rohan-mehta","phone:9876543210","USES","FIR-2025-041"),("person:vikram-shah","phone:9876543210","USES","FIR-2025-063"),
 ("person:rohan-mehta","vehicle:dl8cab1234","ASSOCIATED_WITH","FIR-2025-041"),("person:vikram-shah","vehicle:dl8cab1234","ASSOCIATED_WITH","FIR-2025-063"),
 ("person:rohan-mehta","location:eastern-freight-warehouse","SEEN_AT","FIR-2025-041"),("person:vikram-shah","location:eastern-freight-warehouse","SEEN_AT","FIR-2025-063"),
 ("person:ayesha-khan","person:rohan-mehta","MET_WITH","INT-2025-088"),("account:001234567890","organization:orion-logistics","CONNECTED_TO","INT-2025-088"),
 ("person:rohan-mehta","person:vikram-shah","CONTACTED","FIR-2025-041")
]

