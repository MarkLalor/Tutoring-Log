//On page load.
$(function($)
{
	loadTutors();
	
	$(".view-log").click(function(){
		if ($(this).attr('data-which') == 'club-member')
		{
			loadTutor($("#club-member").val())
		}
	});
	
	$(".download-excel").click(function(){
		window.open('/request?query=tutor&email=' + encodeURIComponent($("#club-member").val()) + '&type=csv', '_blank');
	});
	
	$(".printable-report").click(function(){
		window.open('/request?query=tutor&email=' + encodeURIComponent($("#club-member").val()) + '&type=pdf', '_blank');
	});
});

function loadTutors()
{
	//Retrieve tutor list
	$.ajax({
		type: "GET",
		data: {'r': 'tutors'},
		url: "request",
		dataType: "text",
		success: function(data) {
			$('#club-member').append('<option disabled selected value = "" style = "display: none;"> -- select a tutor -- </option>');
			var parsed = JSON.parse(data);  
			parsed.map(function(obj) {
				$('#club-member').append($("<option></option>").attr("value", obj['email']).text(obj['last'] + ', ' + obj['first'] + ', ' + obj['email']));
			});
			$("#tutors-loading").remove();
		}
	});
}

function loadTutor(email)
{
	$('#data-table').empty();
	$.ajax({
		type: "GET",
		data: {'query': 'tutor', 'email': email},
		url: "request",
		dataType: "text",
		success: function(data) {
			$('#data-table').append('<thead><tr><td><input type = "checkbox" id = "data-select-all" /></td><td>Tutee Name</td><td>Tutee Email</td><td>Subject</td><td>Date</td><td>Minutes</td><td>Satisfaction</td><td>Comments</td><td>Session ID</td></tr></thead>');
			var parsed = JSON.parse(data);
			var keys = ["tutee_name", "tutee_email", "subject", "date_tutored", "minutes", "satisfaction", "comments", "id"];
			var body = $('<tbody></tbody>');
			var total_minutes = 0;
			for (var i = 0; i < parsed["tutee_name"].length; i++)
			{
				var row = $('<tr></tr>');
				row.append($('<td></td>').attr('class', 'data-select').append('<input type = "checkbox" data-id = "' + parsed['id'][i] + '" />'))
				var j;
				for (j = 0; j < keys.length; j++) {
				    var key = keys[j];
				    var content = null;
				    if (key == 'comments')
				    	content = '<div style="max-width: 180px; max-height: 80px; overflow: auto;">' + parsed[key][i] + '</div>';
					else
						content = parsed[key][i];
				    
				    if (key == 'minutes')
				    	total_minutes += parseInt(parsed[key][i]);
				    
				    row.append($('<td></td>').attr('class', 'data-' + key).html(content));
				}
				body.append(row);
			}
			$('#data-table').append(body);
			
			$('#data-time').html(format_minutes(total_minutes))
		}
	});
}

function format_minutes(time)
{
	hours = Math.floor(time/60);
    minutes = time % 60;
    return String(hours) + (hours > 0 ? (hours > 1 ? ' hours' : ' hour') : '') + ' ' + String(minutes) + (minutes > 0 ? (minutes > 1 ? ' minutes' : ' minute') : '');
}