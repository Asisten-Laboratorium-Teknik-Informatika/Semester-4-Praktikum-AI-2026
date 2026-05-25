from app.services.safety import check_crisis


hasil = check_crisis("ingin mati rasanya")
assert hasil is not None, "GAGAL: krisis tidak terdeteksi!"

hasil = check_crisis("hari ini capek banget")
assert hasil is None, "GAGAL: kalimat normal dianggap krisis!"

print("Safety layer berfungsi dengan benar")
