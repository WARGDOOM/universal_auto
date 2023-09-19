// SIDEBAR TOGGLE

let sidebarOpen = false;
let sidebar = document.getElementById("sidebar");

// Визначте змінну для стану бічного бару

function toggleSidebar() {
	const sidebar = document.getElementById("sidebar");

	if (sidebarOpen) {
		// Закрити бічний бар
		sidebar.classList.remove("sidebar-responsive");
		sidebarOpen = false;
	} else {
		// Відкрити бічний бар
		sidebar.classList.add("sidebar-responsive");
		sidebarOpen = true;
	}
}


// ---------- CHARTS ----------

// BAR CHART
let barChartOptions = {
	series: [{
		data: [],
		name: "Дохід: ",
	}],
	chart: {
		type: "bar",
		background: "transparent",
		height: 350,
		toolbar: {
			show: false,
		},
	},
	colors: [
		"#89A632",
		"#FDCA10",
		"#18A64D",
		"#1858A6",
		"#79C8C5",
		"#EC6323",
		"#018B72"
	],
	plotOptions: {
		bar: {
			distributed: true,
			borderRadius: 4,
			horizontal: false,
			columnWidth: "40%",
		}
	},
	dataLabels: {
		enabled: false,
	},
	fill: {
		opacity: 1,
	},
	grid: {
		borderColor: "#55596e",
		yaxis: {
			lines: {
				show: true,
			},
		},
		xaxis: {
			lines: {
				show: true,
			},
		},
	},
	legend: {
		labels: {
			colors: "#f5f7ff",
		},
		show: false,
		position: "top",
	},
	stroke: {
		colors: ["transparent"],
		show: true,
		width: 2
	},
	tooltip: {
		shared: true,
		intersect: false,
		theme: "dark",
	},
	xaxis: {
		categories: [],
		title: {
			style: {
				color: "#f5f7ff",
			},
		},
		axisBorder: {
			show: true,
			color: "#55596e",
		},
		axisTicks: {
			show: true,
			color: "#55596e",
		},
		labels: {
			style: {
				colors: "#f5f7ff",
			},
			rotate: -45,
		},
	},
	yaxis: {
		title: {
			text: gettext("Дохід (грн.)"),
			style: {
				color: "#f5f7ff",
			},
		},
		axisBorder: {
			color: "#55596e",
			show: true,
		},
		axisTicks: {
			color: "#55596e",
			show: true,
		},
		labels: {
			style: {
				colors: "#f5f7ff",
			},
		},
	}
};

let barChart = new ApexCharts(document.querySelector("#bar-chart"), barChartOptions);
barChart.render();


// AREA CHART
let areaChartOptions = {
	series: [{
		name: "",
		data: [''],
	}, {
		name: "",
		data: [''],
	}],
	chart: {
		type: "area",
		background: "transparent",
		height: 350,
		stacked: false,
		toolbar: {
			show: false,
		},
	},
	colors: [
		"#DCE43F",
		"#89A632",
		"#018B72",
		"#79C8C5",
		"#EC6323",
		"#1858A6",
		"#FDCA10"
	],
	labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul"],
	dataLabels: {
		enabled: false,
	},
	fill: {
		gradient: {
			opacityFrom: 0.4,
			opacityTo: 0.1,
			shadeIntensity: 1,
			stops: [0, 100],
			type: "vertical",
		},
		type: "gradient",
	},
	grid: {
		borderColor: "#55596e",
		yaxis: {
			lines: {
				show: true,
			},
		},
		xaxis: {
			lines: {
				show: true,
			},
		},
	},
	legend: {
		labels: {
			colors: "#f5f7ff",
		},
		show: true,
		position: "top",
		horizontalAlign: 'left',
	},
	markers: {
		size: 6,
		strokeColors: "#1b2635",
		strokeWidth: 3,
	},
	stroke: {
		curve: "smooth",
	},
	xAxis: {
		axisBorder: {
			color: "#55596e",
			show: true,
		},
		axisTicks: {
			color: "#55596e",
			show: true,
		},
		labels: {
			offsetY: 5,
			style: {
				colors: "#f5f7ff",
			},
		},
	},
	yAxis:
		[
			{
				title: {
					text: "пробіг км",
					style: {
						color: "#f5f7ff",
					},
				},
				labels: {
					style: {
						colors: ["#f5f7ff"],
					},
				},
			},
			{
				opposite: true,
				title: {
					text: "пробіг км",
					style: {
						color: "#f5f7ff",
					},
				},
				labels: {
					style: {
						colors: ["#f5f7ff"],
					},
				},
			},
		],
	tooltip: {
		shared: true,
		intersect: false,
		theme: "dark",
	}
};

let areaChart = new ApexCharts(document.querySelector("#area-chart"), areaChartOptions);
areaChart.render();

$(document).ready(function () {

	// Обробка графіків
	function loadDefaultKasa(period) {
		$.ajax({
			type: "GET",
			url: ajaxGetUrl,
			data: {
				action: 'get_cash_partner',
				period: period
			},
			success: function (response) {
				let data = response.data[0];
				let totalAmount = parseFloat(response.data[1]).toFixed(2);
				let totalDistance = parseFloat(response.data[2]).toFixed(2);
				let startDate = response.data[3];
				let endDate = response.data[4];
				let efficiency = parseFloat(response.data[5]).toFixed(2);
				let formattedData = {};

				Object.keys(data).forEach(function (key) {
					let value = parseFloat(data[key]).toFixed(2);
					if (value > 0) {
						let formattedKey = key;
						formattedData[formattedKey] = value;
					}
				});

				let sortedKeys = Object.keys(formattedData).sort();
				let sortedFormattedData = {};
				sortedKeys.forEach(function (key) {
					sortedFormattedData[key] = formattedData[key];
				});

				barChartOptions.series[0].data = Object.values(sortedFormattedData);
				barChartOptions.xaxis.categories = Object.keys(sortedFormattedData);
				barChart.updateOptions(barChartOptions);

				$('.weekly-income-dates').text(startDate + ' ' + gettext('по') + ' ' + endDate);
				$('.weekly-income-rent').text(totalDistance + ' ' + gettext('км'));
				$('.weekly-income-amount').text(totalAmount + ' ' + gettext('грн'));
				$('.income-efficiency').text(efficiency + ' ' + gettext('грн/км'));

			}
		});
	}

	function loadEffectiveChart(period) {
		$.ajax({
			type: "GET",
			url: ajaxGetUrl,
			data: {
				action: 'partner',
				period: period,
			},
			success: function (response) {
				let dataObject = response.data;
				let carData = {};

				// Проходимося по кожному ідентифікатору автомобіля
				Object.keys(dataObject).forEach(function (carNumber) {
					carData[carNumber] = dataObject[carNumber].map(function (item) {
						return {
							date: new Date(item.date_effective),
							efficiency: parseFloat(item.efficiency)
						};
					});
				});

				let mileageSeries = Object.keys(carData).map(function (carNumber) {
					return {
						name: carNumber,
						data: carData[carNumber].map(function (entry) {
							return entry.efficiency;
						})
					};
				});

				let dates = carData[Object.keys(carData)[0]].map(function (entry) {
					return `${entry.date.getDate()}-${entry.date.getMonth() + 1}-${entry.date.getFullYear()}`;
				});

				// Оновити опції графіка з новими даними
				areaChartOptions.series = mileageSeries;
				areaChartOptions.labels = dates;

				areaChart.updateOptions(areaChartOptions);
			}
		});
	}

	const commonPeriodSelect = $('#period-common');
	const showCommonButton = $('#common-show-button');

	showCommonButton.on('click', function (event) {
		event.preventDefault();

		const selectedPeriod = commonPeriodSelect.val();
		loadDefaultKasa(selectedPeriod);
		loadEffectiveChart(selectedPeriod);
	});

	loadDefaultKasa('yesterday');
	loadEffectiveChart('current_week');
});

$(document).ready(function () {

	const partnerForm = $("#partnerForm");
	const partnerLoginField = $("#partnerLogin");
	const partnerRadioButtons = $("input[name='partner']");

	var uklonStatus = localStorage.getItem('uklon');
	var boltStatus = localStorage.getItem('bolt');
	var uberStatus = localStorage.getItem('uber');

	// Перевірка умови, коли показувати або ховати елемент
	if ((uklonStatus === 'success' || boltStatus === 'success' || uberStatus === 'success')) {
		// Показуємо елемент
		$("#updateDatabase").show();
	} else {
		// Ховаємо елемент
		$("#updateDatabase").hide();
	}

	partnerRadioButtons.change(function () {
		const selectedPartner = $("input[name='partner']:checked").val();
		updateLoginField(selectedPartner);
	});

	function updateLoginField(partner) {
		if (partner === 'uklon') {
			partnerLoginField.val('+380');
		} else {
			partnerLoginField.val('');
			$("#partnerPassword").val("");
		}
	}

	if (sessionStorage.getItem('settings') === 'true') {
		$("#settingsWindow").fadeIn();
	}

	if (localStorage.getItem('uber')) {
		$("#partnerLogin").hide()
		$("#partnerPassword").hide()
		$(".opt-partnerForm").hide()
		$(".login-ok").show()
		$("#loginErrorMessage").hide()
	}

	$("#settingBtnContainer").click(function () {
		sessionStorage.setItem('settings', 'true');
		$("#settingsWindow").fadeIn();
	});

	$(".sidebar-list-item.admin").on("click", function () {

		var adminPanelURL = $(this).data("url");

		if (adminPanelURL) {
			window.open(adminPanelURL, "_blank");
		}
	});

	$(".close-btn").click(function () {
		$("#settingsWindow").fadeOut();
		sessionStorage.setItem('settings', 'false');
		location.reload();
	});

	$(".login-btn").click(function () {
		const selectedPartner = partnerForm.find("input[name='partner']:checked").val();
		const partnerLogin = partnerForm.find("#partnerLogin").val();
		const partnerPassword = partnerForm.find("#partnerPassword").val();

		if (partnerForm[0].checkValidity() && selectedPartner) {
			showLoader(partnerForm);
			sendLoginDataToServer(selectedPartner, partnerLogin, partnerPassword);
		}
	});

	$(".logout-btn").click(function () {
		const selectedPartner = partnerForm.find("input[name='partner']:checked").val();
		sendLogautDataToServer(selectedPartner);
		localStorage.removeItem(selectedPartner);
		$("#partnerLogin").show()
		$("#partnerPassword").show()
		$(".opt-partnerForm").show()
		$(".login-ok").hide()
		$("#loginErrorMessage").hide()
	});

	// Show/hide password functionality
	$("#showPasswordPartner").click(function () {
		let $checkbox = $(this);
		let $passwordField = $checkbox.closest('.settings-content').find('.partnerPassword');
		let change = $checkbox.is(":checked") ? "text" : "password";
		$passwordField.prop('type', change);
	});

	function showLoader(form) {
		$(".opt-partnerForm").hide();
		form.find(".loader-login").show();
		$("input[name='partner']").prop("disabled", true);
	}

	function hideLoader(form) {
		form.find(".loader-login").hide();
		$("input[name='partner']").prop("disabled", false);
	}


	$('[name="partner"]').change(function () {
		let partner = $(this).val()
		let login = localStorage.getItem(partner)

		if (login === "success") {
			$("#partnerLogin").hide()
			$("#partnerPassword").hide()
			$(".opt-partnerForm").hide()
			$(".login-ok").show()
			$("#loginErrorMessage").hide()
		} else {
			$("#partnerLogin").show()
			$("#partnerPassword").show()
			$(".opt-partnerForm").show()
			$(".login-ok").hide()
			$("#loginErrorMessage").hide()
		}
	})

	function sendLoginDataToServer(partner, login, password) {
		$.ajax({
			type: "POST",
			url: ajaxPostUrl,
			data: {
				csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val(),
				action: partner,
				login: login,
				password: password,
			},
			success: function (response) {
				if (response.data === true) {
					localStorage.setItem(partner, 'success');
					$("#partnerLogin").hide()
					$("#partnerPassword").hide().val('')
					$(".opt-partnerForm").hide()
					$(".login-ok").show()
					$("#loginErrorMessage").hide()
				} else {
					$(".opt-partnerForm").show();
					$("#loginErrorMessage").show()
					$("#partnerLogin").val("").addClass("error-border");
					$("#partnerPassword").val("").addClass("error-border");
				}
				hideLoader(partnerForm);
			}
		});
	}

	function sendLogautDataToServer(partner) {
		$("#partnerLogin").val("")
		$("#partnerPassword").val("")
		$.ajax({
			type: "POST",
			url: ajaxPostUrl,
			data: {
				csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val(),
				action: partner + "_logout",
			},
			success: function (response) {
				if (response.data === true) {
					localStorage.setItem(partner, 'false');
					$("#partnerLogin").show()
					$("#partnerPassword").show()
					$(".opt-partnerForm").show()
					$(".login-ok").hide()
				}
			}
		});
	}

	$("#updateDatabaseContainer").click(function () {

		$("#loadingModal").css("display", "block")

		$.ajax({
			type: "POST",
			url: ajaxPostUrl,
			data: {
				csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val(),
				action: "upd_database",
			},
			success: function (response) {
				if (response.data === true) {
					$("#loadingMessage").text(gettext("База даних оновлено"));
					$("#loader").css("display", "none");
					$("#checkmark").css("display", "block");

					setTimeout(function () {
						$("#loadingModal").css("display", "none");
						window.location.reload();
					}, 3000);
				} else {
					$("#loadingMessage").text(gettext("Помилка оновлення бази даних. Спробуйте пізніше або зверніться до адміністратора"));

					setTimeout(function () {
						$("#loadingModal").css("display", "none");
						window.location.reload();
					}, 3000);
				}
			}
		});
	});
});

$(document).ready(function () {

	$.ajax({
		url: ajaxGetUrl,
		type: "GET",
		data: {
			action: "is_logged_in"
		},
		success: function (data) {
			if (data.is_logged_in === true) {
				let userName = data.user_name;
				$("#account_circle").text(userName).show();
				$("#logout-dashboard").show();
			}
		}
	})

	$("#logout-dashboard").click(function () {
		$.ajax({
			type: "POST",
			url: ajaxPostUrl,
			data: {
				csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val(),
				action: "logout_invest",
			},
			success: function (response) {
				if (response.logged_out === true) {
					window.location.href = "/";
				}
			}
		});
	});

	// change-password

	$("#changePassword").click(function () {
		$("#passwordChangeForm").toggle();
	});


	$("#submitPassword").click(function () {
		let password = $("#oldPassword").val();
		let newPassword = $("#newPassword").val();
		let confirmPassword = $("#confirmPassword").val();

		if (newPassword !== confirmPassword) {
			$("#ChangeErrorMessage").show();
		} else {
			$.ajax({
				url: ajaxPostUrl,
				type: 'POST',
				data: {
					action: 'change_password',
					password: password,
					newPassword: newPassword,
					csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val()
				},
				success: function (response) {
					if (response.data['success'] === true) {
						$("#passwordChangeForm").hide();
						window.location.href = "/";
					} else {
						$("#oldPasswordMessage").show();
					}
				}
			});
		}
	});
	// burger-menu
	$('.burger-menu').click(function () {
		$('.burger-menu').toggleClass('open');
	});

	$('#partnerVehicleBtnContainer').click(function () {
		$('.payback-car').show();
		$('.payback-car').css('display', 'flex');
		$('.charts').hide();
		$('.main-cards').hide();
		$('.info-driver').hide();
		$('.common-period').hide();
	});

	$('#partnerDriverBtnContainer').click(function () {
		$('.info-driver').show();
		$('.payback-car').hide();
		$('.charts').hide();
		$('.main-cards').hide();
		$('.common-period').hide();
	});

	$(".close-btn").click(function () {
		$("#settingsWindow").fadeOut();
		sessionStorage.setItem('settings', 'false');
		location.reload();
	});
});

$(document).ready(function () {
	const periodSelect = $('#period');
	const showButton = $('#show-button');
	const partnerDriverBtn = $('#partnerDriverBtn');

	periodSelect.val("day");

	partnerDriverBtn.on('click', function (event) {
		showButton.click();
	});

	showButton.on('click', function (event) {
		event.preventDefault();

		const selectedPeriod = periodSelect.val();

		$.ajax({
			type: "GET",
			url: ajaxGetUrl,
			data: {
				action: 'get_drivers_partner',
				period: selectedPeriod
			},
			success: function (response) {
				let table = $('.info-driver table');
				table.find('tr:gt(0)').remove();

				response.data.forEach(function (item) {
					let row = $('<tr></tr>');

					row.append('<td>' + item.driver + '</td>');
					row.append('<td>' + item.total_kasa + '</td>');
					row.append('<td>' + item.total_orders + '</td>');
					row.append('<td>' + item.accept_percent + " %" + '</td>');
					row.append('<td>' + item.average_price + '</td>');
					row.append('<td>' + item.mileage + '</td>');
					row.append('<td>' + item.efficiency + '</td>');
					row.append('<td>' + item.road_time + '</td>');

					table.append(row);
				});
			}
		});
	});
});

function showDatePicker() {
	var periodSelect = document.getElementById("period");
	var datePicker = document.getElementById("datePicker");

	if (periodSelect.value === "custom") {
		datePicker.style.display = "block";
	} else {
		datePicker.style.display = "none";
	}
}

function applyCustomDateRange() {
	var startDate = document.getElementById("start_date").value;
	var endDate = document.getElementById("end_date").value;
}