// Copyright (c) 2023, Hussain Nagaria and contributors
// For license information, please see license.txt

frappe.query_reports["FF Assignment Summary By Student"] = {
  filters: [],
  formatter: function (value, row, column, data, default_formatter) {
    // if value is "Failed" make it red
    if (value == "Failed") {
      value = `<span style="color: red;">${value}</span>`;
    } else if (value == "Passed") {
      value = `<span style="color: green;">${value}</span>`;
    } else if (value == "Unchecked") {
      value = `<span style="color: orange;">${value}</span>`;
    } else if (value == "Check In Progress") {
      value = `<span style="color: blue;">${value}</span>`;
    }
    
    return default_formatter(value, row, column, data);
  },
};
