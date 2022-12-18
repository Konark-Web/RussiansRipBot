import requests
import random


def get_stat_from_api():
    response = requests.get('https://russianwarship.rip/api/v1/statistics/latest')

    response_data = response.json()['data']
    day_war = response_data['day']
    date = response_data['date']
    personnel_units = response_data['stats']['personnel_units']
    tanks = response_data['stats']['tanks']
    armoured_fighting_vehicles = response_data['stats']['armoured_fighting_vehicles']
    artillery_systems = response_data['stats']['artillery_systems']
    mlrs = response_data['stats']['mlrs']
    aa_warfare_systems = response_data['stats']['aa_warfare_systems']
    planes = response_data['stats']['planes']
    helicopters = response_data['stats']['helicopters']
    vehicles_fuel_tanks = response_data['stats']['vehicles_fuel_tanks']
    warships_cutters = response_data['stats']['warships_cutters']
    cruise_missiles = response_data['stats']['cruise_missiles']
    uav_systems = response_data['stats']['uav_systems']
    special_military_equip = response_data['stats']['special_military_equip']
    atgm_srbm_systems = response_data['stats']['atgm_srbm_systems']

    personnel_units_increase_text = ''
    if personnel_units_increase := response_data['increase']['personnel_units']:
        personnel_units_increase_text = f' <b>(+ {personnel_units_increase})</b>'

    tanks_increase_text = ''
    if tanks_increase := response_data['increase']['tanks']:
        tanks_increase_text = f' <b>(+ {tanks_increase})</b>'

    afv_increase_text = ''
    if armoured_fighting_vehicles_increase := response_data['increase']['armoured_fighting_vehicles']:
        afv_increase_text = f' <b>(+ {armoured_fighting_vehicles_increase})</b>'

    artillery_systems_increase_text = ''
    if artillery_systems_increase := response_data['increase']['artillery_systems']:
        artillery_systems_increase_text = f' <b>(+ {artillery_systems_increase})</b>'

    mlrs_increase_text = ''
    if mlrs_increase := response_data['increase']['mlrs']:
        mlrs_increase_text = f' <b>(+ {mlrs_increase})</b>'

    aa_warfare_systems_increase_text = ''
    if aa_warfare_systems_increase := response_data['increase'][
        'aa_warfare_systems']:
        aa_warfare_systems_increase_text = f' <b>(+ {aa_warfare_systems_increase})</b>'

    planes_increase_text = ''
    if planes_increase := response_data['increase']['planes']:
        planes_increase_text = f' <b>(+ {planes_increase})</b>'

    helicopters_increase_text = ''
    if helicopters_increase := response_data['increase']['helicopters']:
        helicopters_increase_text = f' <b>(+ {helicopters_increase})</b>'

    vehicles_fuel_tanks_increase_text = ''
    if aa_warfare_systems_increase := response_data['increase']['vehicles_fuel_tanks']:
        vehicles_fuel_tanks_increase_text = f' <b>(+ {aa_warfare_systems_increase})</b>'

    warships_cutters_increase_text = ''
    if warships_cutters_increase := response_data['increase']['warships_cutters']:
        warships_cutters_increase_text = f' <b>(+ {warships_cutters_increase})</b>'

    cruise_missiles_increase_text = ''
    if cruise_missiles_increase := response_data['increase']['cruise_missiles']:
        cruise_missiles_increase_text = f' <b>(+ {cruise_missiles_increase})</b>'

    uav_systems_increase_text = ''
    if uav_systems_increase := response_data['increase']['uav_systems']:
        uav_systems_increase_text = f' <b>(+ {uav_systems_increase})</b>'

    special_military_equip_increase_text = ''
    if special_military_equip_increase := response_data['increase']['special_military_equip']:
        special_military_equip_increase_text = f' <b>(+ {special_military_equip_increase})</b>'

    atgm_srbm_systems_increase_text = ''
    if atgm_srbm_systems_increase := response_data['increase']['atgm_srbm_systems']:
        atgm_srbm_systems_increase_text = f' <b>(+ {atgm_srbm_systems_increase})</b>'

    names_for_rus = ['Хороших русских', 'На концерті Кобзона',
                     'Зробило жест доброї волі']
    rus_name = random.choice(names_for_rus)

    return f'<b>{day_war} ДЕНЬ ВІЙНИ ({date})</b>\n\n'\
           f'<b>{rus_name} ☠️:</b> {personnel_units}{personnel_units_increase_text}\n' \
           f'<b>Танків:</b> {tanks}{tanks_increase_text}\n' \
           f'<b>ББМ:</b> {armoured_fighting_vehicles}{afv_increase_text}\n' \
           f'<b>Арт. систем:</b> {artillery_systems}{artillery_systems_increase_text}\n' \
           f'<b>РСЗВ:</b> {mlrs}{mlrs_increase_text}\n' \
           f'<b>Засобів ППО:</b> {aa_warfare_systems}{aa_warfare_systems_increase_text}\n' \
           f'<b>Літаків:</b> {planes}{planes_increase_text}\n' \
           f'<b>Гелікоптерів:</b> {helicopters}{helicopters_increase_text}\n' \
           f'<b>Автотехніки:</b> {vehicles_fuel_tanks}{vehicles_fuel_tanks_increase_text}\n' \
           f'<b>Морського транспорту:</b> {warships_cutters}{warships_cutters_increase_text}\n' \
           f'<b>БПЛА:</b> {uav_systems}{uav_systems_increase_text}\n' \
           f'<b>Спец. техніки:</b> {special_military_equip}{special_military_equip_increase_text}\n' \
           f'<b>ОТРК/ТРК:</b> {atgm_srbm_systems}{atgm_srbm_systems_increase_text}\n' \
           f'<b>Крилатих ракет:</b> {cruise_missiles}{cruise_missiles_increase_text}\n\n\n' \
           f'<i>Не забувайте донатити ЗСУ! -> /donate</i>\n' \
           f'<i>СЛАВА УКРАЇНІ 🇺🇦, СЛАВА НАЦІЇ і піздєц російській федерації 🐖</i>'
