
import operator
import math
import csv
import time

class Jobs:  # işlere ait sınıfı göstermektedir.
    name = ""  # işin adının göstermektedir.
    agent_name = ""  # işin hangi ajana ait olduğunu göstermektedir.
    process_time = 0.0  # işin gerçek proses süresini göstermektedir.
    weight = 0  # işin öneminin bir ifadesi olan ağırlığı vermektedir.
    revised_weight = 0  # ağırlığın ajan best ve worst değerlerine göre normalize edilmiş hali
    deadline = 0  # işe ait son teslim tarihini göstermektedir.
    position = 0  # işin çizelgedeki sırasını göstermektedir.
    completion_time = 0.0  # işin çizelegedeki sırasına göre tamamlanma zamanının gösterir.
    WPT = 0.0  # işin ağırlıklandırılmış proses süresini gösterir.
    positioned_process_time = 0.0  # işin çizelgdki sırasına göre öğrnme-bozlma altında process süresini göstermektedir.
    revised_process_time = 0.0  # işin belirlenmiş olan sezgisele göre hesaplanmış proses süresini göstermektedir.
    tardy = 0  # işin tardy durumuna düşüp düşmediğini gösterir. düşmüyorsa 0 düşüyorsa 1 dir.
    agent_code = 0  # işin ait olduğu ajanın kodunu vermektedir. A ajanı 0 B ajanı için 1 olmaktadır.


class Agents:  # işlerin ait olduğu ajan sınıfını göstermektedir.
    def __init__(self, name):
        self.name = name  # ajanının adını göstermektedir.

    num_of_jobs = 0  # ajana ait kaç iş olduğunu göstermektedir.
    job_list = []  # ajana ait işlerin listesini vermektedir.
    object = 0.0  # çizelge ile elde edilen normalize edilmiş amaç fonksiyonu değerini vermektedir.


class Node:  # düğümlere ait sınıfı göstermektedir.
    assigned_jobs = []  # düğümdeki işleri gösterir.
    unassigned_jobs = []
    tamamlanma = 0.0  # düğümün son işinin tamamlanma zamanını gösterir.
    a_amac = 0.0  # düğümde A ajanına ait işlerin tamamlanma zamanını gösteririr
    b_amac = 0.0  # düğümde A ajanına ait işlerin tamamlanma zamanını gösteririr
    is_isim = []  # düğümdeki işlerin isimlerini gösterir.
    unassigned_is_isim = []
    is_sayisi = 0  # dğümdeki iş sayısını verir.
    LB = 0.0


def jobs_info():
    # işlere ait bilgiler girilir
    print("A ajanının amacı KENDİSİNE AİT İŞLERİN toplam ağırlıklı tamamlanma zamanının minimizasyonudur.")
    print("B ajanının amacı hiç bir işin TARDY duruma düşmemesidir.")
    num_of_jobs = int(input("Tüm iş sayısını giriniz: "))  # toplam iş sayısını vemektedir.
    print("Lütfen ilk olarak A ajanına ait işlerin bilgilerini giriniz:")
    A.num_of_jobs = int(input("A ajanına ait iş sayısını giriniz: "))  # A ajanına ait iş sayısını bermektedir.
    A.job_list = []
    B.num_of_jobs = num_of_jobs - A.num_of_jobs
    B.job_list = []
    for _ in range(0, num_of_jobs):
        job = Jobs()
        if _ < A.num_of_jobs:
            print("A ajanına ait {}. iş bilgilerini giriyorsunuz: ".format((_ + 1)))
            job.agent_name = "A"
            job.agent_code = 0
            A.job_list.append(job)
        else:
            print("B ajanına ait {}. iş bilgilerini giriyorsunuz: ".format((_ + 1 - A.num_of_jobs)))
            job.agent_name = "B"
            job.agent_code = 1
            B.job_list.append(job)
        job.name = input("işin adını giriniz: ")
        job.process_time = float(input("işin proses süresini giriniz: "))
        job.weight = float(input("işin ağırlığını giriniz: "))
        job.deadline = float(input("işin deadline bilgisini giriniz: "))
        job.WPT = job.process_time / job.weight
        _ = _ + 1
    print("..............")
    A.job_list = sorted(A.job_list, key=operator.attrgetter("WPT"))
    B.job_list = sorted(B.job_list, key=operator.attrgetter("deadline"))
    all_jobs_info = A.job_list + B.job_list  # Hem A hem de B ajanına ait tüm işlerin listesidir.
    return all_jobs_info


def job_analyze(job_list):
    # B ajanına ait işlerin slack timenına ortalama kaç tane A ajanına ait işin sığdığını hesağlar
    """
    :param job_list: iş listesi
    :return: jobs_ratio isimli bir dictionary
    """
    job_list = sorted(job_list, key=operator.attrgetter("process_time"))
    total_jobs_list = []
    for job in job_list:
        jobs = job_list.copy()
        jobs.remove(job)
        slack_time = job.deadline - job.process_time
        number = 0
        for jobb in jobs:
            slack_time = slack_time - jobb.process_time
            if slack_time >= 0:
                number = number + 1
        total_jobs_list.append(number)
    Sum = sum(total_jobs_list)
    medium = Sum / len(job_list)
    maks = max(total_jobs_list)
    jobs_ratio = {"medium": medium, "max": maks}
    return jobs_ratio


def calculate_learning_coefficient(learning_percent):
    """
    :param learning_percent: öğrenme yüzdesi
    :return: learning_coefficient: öğrenme katsayısı
    """
    learning_coefficient = (math.log(learning_percent)) / (math.log(2))  # öğrenme katsayısı
    return learning_coefficient


def calculate_positioned_process_time(jobb, position, completion_time, learning_rate, deterioration_rate):
    # bir işin öğreneme ve bozulma etkileri altında pozisyon bazlı proses süresini hesaplar.
    """
    :param jobb: proses süresi hesaplanacak iş
    :param position: proses süresi hesaplanacak işin çizelgede bulunduğu sıra
    :param completion_time: çizelgedeki proses süresi hesaplanacak işten hemen önceki işin tamamlanma zamanı
    :param learning_rate: öğrenme katsayısı
    :param deterioration_rate: bozulma katsayısı
    :return: jobb.positioned_process_time: pozisyon bazlı proses süresi
    """
    jobb.position = position
    jobb.positioned_process_time = ((jobb.process_time + deterioration_rate * completion_time) *
                                    (jobb.position ** learning_rate))  # işin pozisyona bağlı iş süresini gösterir.
    #  print("{} gerçek proses süresi {} iken {}. sıraya atanınca pozisyon bazlı proses süresi {} olmaktadır."
    #  .format(jobb, jobb.process_time, jobb.position, jobb.positioned_process_time))
    return jobb.positioned_process_time


def calculate_job_PD(job_list, position, complete_time, learning_rate, deterioration_rate, interpolation_rate):
    #  belirli bir pozisyon için en küçük revize proses süreni çizelgenin başıa alarak yeni çizelge oluşturur.
    """
    :param job_list: PD değerleri hesaplanacak iş listesi
    :param position: PD değerinin hesaplanacağı ve en küçük PD değerine sahip işin atanacağı sıra
    :param complete_time: PD değerinin hesaplanacağı ve en küçük PD değerine sahip işe başlanacak zamana
    :param learning_rate: öğrenme katsayısı
    :param deterioration_rate: bozulma katsayısı
    :param interpolation_rate: interpolasyon katsayısı
    :return: schedule : PD değerlerine göre en küçük iş başlangıçta olan çizelge
    """
    completion_time = complete_time  # çizelgedeki son işin tamamlanma zamanını göstermektedir.
    schedule = []
    for jobb in job_list:
        calculate_positioned_process_time(jobb, position, completion_time, learning_rate, deterioration_rate)
        jobb.completion_time = completion_time + jobb.positioned_process_time
        jobb.revised_process_time = (interpolation_rate * jobb.positioned_process_time + (1 - interpolation_rate) *
                                     jobb.deadline) * jobb.agent_code + (jobb.positioned_process_time *
                                                                         (1 - jobb.agent_code) / jobb.weight)
        print("{} işi için PD değeri, {}. pozisyon için {} olmaktadır.".format(jobb.name, position, jobb.revised_process_time))
    job_list = sorted(job_list, key=operator.attrgetter("revised_process_time"))  # her bir pozisyon için PD
    # değerleri hesaplanan job_list teki işler  "revised_process_time" attributelarına göre sıralanır.
    print("en küçük PD değerine sahip iş {} dir". format(job_list[0].name))
    schedule.append(job_list[0])
    job_list.remove(job_list[0])
    schedule = schedule + job_list
    return schedule


def calculate_job_PD_all_agents(job_list, position, complete_time, learning_rate, deterioration_rate):
    #  revize proses sürelerine göre sıralanmış işlere ait çizelgeyi oluşturur.
    """
    :param job_list: PD değerleri hesaplanacak iş listesi
    :param position: PD değerinin hesaplanacağı ve en küçük PD değerine sahip işin atanacağı sıra
    :param complete_time: PD değerinin hesaplanacağı ve en küçük PD değerine sahip işe başlanacak zamana
    :param learning_rate: öğrenme katsayısı
    :param deterioration_rate: bozulma katsayısı
    :return: schedule : PD değerlerine göre en küçük iş başlangıçta olan çizelge
    """
    completion_time = complete_time  # çizelgedeki son işin tamamlanma zamanını göstermektedir.
    schedule = []
    for jobb in job_list:
        calculate_positioned_process_time(jobb, position, completion_time, learning_rate, deterioration_rate)
        jobb.completion_time = completion_time + jobb.positioned_process_time
        jobb.revised_process_time = (jobb.positioned_process_time * jobb.agent_code + jobb.positioned_process_time *
                                     (1 - jobb.agent_code)) / jobb.weight
        #  print("{} işi için PD değeri, {}. pozisyon için {} olmaktadır.".format(jobb.name,
        #  position, jobb.revised_process_time))
    job_list = sorted(job_list, key=operator.attrgetter("revised_process_time"))  # her bir pozisyon için PD
    schedule.append(job_list[0])
    job_list.remove(job_list[0])
    schedule = schedule + job_list
    return schedule


def calculate_schedule_by_PD(job_list, position, complete_time, learning_rate, deterioration_rate, interpolation_rate):
    #  revize proses sürelerine göre sıralanmış işlere ait çizelgeyi oluşturur.
    """
    :param job_list: PD değerleri hesaplanacak iş listesi
    :param position: PD değerinin hesaplanacağı ve en küçük PD değerine sahip işin atanacağı sıra
    :param complete_time: PD değerinin hesaplanacağı ve en küçük PD değerine sahip işe başlanacak zamana
    :param learning_rate: öğrenme katsayısı
    :param deterioration_rate: bozulma katsayısı
    :param interpolation_rate: interpolasyon katsayısı
    :return: schedule_by_PD : PD değerlerine göre küçükten büyüğe sıralanmış çizelge
    """

    schedule_by_PD = []  # tüm işlerin revize proses süresine göre listelenmiş halidir.
    completion_time = complete_time  # çizelgedeki son işin tamamlanma zamanını göstermektedir.
    r = position  # PD değerinin hesaplanacağı ve en küçük PD değerine sahip işin atanacağı sıra
    for _ in range(0, len(job_list)):
        for jobb in job_list:
            # for döngüsüyle job_list'teki her iş (jobb) için (position= - + r) pozisyonuna atanması durumunda
            # pozisyon bazlı proses süresi hesaplanır ve PD değeri de diyeceğimiz revised_prcess_time hesaplanır
            position = _ + r  # jobb işinin atanacağı pozisyon
            calculate_positioned_process_time(jobb, position, completion_time, learning_rate, deterioration_rate)
            jobb.completion_time = completion_time + jobb.positioned_process_time
            jobb.revised_process_time = (interpolation_rate * jobb.positioned_process_time +
                                         (1 - interpolation_rate) * jobb.deadline) * jobb.agent_code + \
                                        (jobb.positioned_process_time * (1 - jobb.agent_code) / jobb.weight)
        job_list = sorted(job_list, key=operator.attrgetter("revised_process_time"))  # her bir pozisyon için PD
        # değerleri hesaplanan job_list teki işler  "revised_process_time" attributelarına göre sıralanır.
        schedule_by_PD.append(job_list[0])  # en küçük PD değerine sahip iş schedule_by_PD çizelgesine atanır.
        completion_time = job_list[0].completion_time  # schedule_by_PD çizelgesindeki işin tamamlanma zamanı atanan
        # son işin tamamlanma zamanına eşittir.
        del job_list[0]  # schedule_by_PD çizelgesine atanan iş job_listten silinir.
        _ = + 1
    return schedule_by_PD




def calculate_schedule_by_PD_all_agents(job_list, position, complete_time, learning_rate, deterioration_rate):
    #  revize proses sürelerine göre sıralanmış işlere ait çizelgeyi oluşturur.
    """
    :param job_list: PD değerleri hesaplanacak iş listesi
    :param position: PD değerinin hesaplanacağı ve en küçük PD değerine sahip işin atanacağı sıra
    :param complete_time: PD değerinin hesaplanacağı ve en küçük PD değerine sahip işe başlanacak zamana
    :param learning_rate: öğrenme katsayısı
    :param deterioration_rate: bozulma katsayısı
    :return: schedule_by_PD : PD değerlerine göre küçükten büyüğe sıralanmış çizelge
    """
    schedule_by_PD = []  # tüm işlerin revize proses süresine göre listelenmiş halidir.
    completion_time = complete_time  # çizelgedeki son işin tamamlanma zamanını göstermektedir.
    r = position  # PD değerinin hesaplanacağı ve en küçük PD değerine sahip işin atanacağı sıra
    for _ in range(0, len(job_list)):
        for jobb in job_list:
            # for döngüsüyle job_list'teki her iş (jobb) için (position= - + r) pozisyonuna atanması durumunda
            # pozisyon bazlı proses süresi hesaplanır ve PD değeri de diyeceğimiz revised_prcess_time hesaplanır
            position = _ + r  # jobb işinin atanacağı pozisyon
            jobb.positioned_process_time = calculate_positioned_process_time(jobb, position, completion_time,
                                                                             learning_rate, deterioration_rate)
            jobb.completion_time = completion_time + jobb.positioned_process_time
            jobb.revised_process_time = (jobb.positioned_process_time * jobb.agent_code + jobb.positioned_process_time
                                         * (1 - jobb.agent_code)) / jobb.weight
        job_list = sorted(job_list, key=operator.attrgetter("revised_process_time"))  # her bir pozisyon için PD
        # değerleri hesaplanan job_list teki işler  "revised_process_time" attributelarına göre sıralanır.
        schedule_by_PD.append(job_list[0])  # en küçük PD değerine sahip iş schedule_by_PD çizelgesine atanır.
        completion_time = job_list[0].completion_time  # schedule_by_PD çizelgesindeki işin tamamlanma zamanı atanan
        # son işin tamamlanma zamanına eşittir.
        del job_list[0]  # schedule_by_PD çizelgesine atanan iş job_listten silinir.
        _ = + 1
    return schedule_by_PD


def calculate_schedule_by_PD_all_agents_adjusted_weights(job_list, position, complete_time, a_best, b_best, a_worst,
                                                         b_worst, learning_rate, deterioration_rate):
    #  revize proses süreleri ve revize edilmiş ağırlıklara göre sıralanmış işlere ait çizelgeyi oluşturur.
    """
    :param job_list: PD değerleri hesaplanacak iş listesi
    :param position: PD değerinin hesaplanacağı ve en küçük PD değerine sahip işin atanacağı sıra
    :param complete_time: PD değerinin hesaplanacağı ve en küçük PD değerine sahip işe başlanacak zamana
    :param a_best: A ajanı amacının en iyi değeri
    :param b_best: B ajanı amacının en iyi değeri
    :param a_worst: A ajanı amacının en kötü değeri
    :param b_worst: B ajanı amacının en kötü değeri
    :param learning_rate: öğrenme katsayısı
    :param deterioration_rate: bozulma katsayısı
    :return: schedule_by_PD : PD değerlerine göre küçükten büyüğe sıralanmış çizelge
    """
    schedule_by_PD = []  # tüm işlerin revize proses süresine göre listelenmiş halidir.
    completion_time = complete_time  # çizelgedeki son işin tamamlanma zamanını göstermektedir.
    r = position  # PD değerinin hesaplanacağı ve en küçük PD değerine sahip işin atanacağı sıra
    for _ in range(0, len(job_list)):
        for jobb in job_list:
            # for döngüsüyle job_list'teki her iş (jobb) için (position= - + r) pozisyonuna atanması durumunda
            # pozisyon bazlı proses süresi hesaplanır ve PD değeri de diyeceğimiz revised_prcess_time hesaplanır
            if jobb.agent_name == "A":
                if b_worst == b_best:
                    jobb.revised_weight = jobb.weight
                else:
                    jobb.revised_weight = jobb.weight * (b_worst - b_best)
            else:
                if a_worst == a_best:
                    jobb.revised_weight = jobb.weight
                else:
                    jobb.revised_weight = jobb.weight * (a_worst - a_best)
            position = _ + r  # jobb işinin atanacağı pozisyon
            jobb.positioned_process_time = calculate_positioned_process_time(jobb, position, completion_time,
                                                                             learning_rate, deterioration_rate)
            jobb.completion_time = completion_time + jobb.positioned_process_time
            jobb.revised_process_time = (jobb.positioned_process_time * jobb.agent_code + jobb.positioned_process_time
                                         * (1 - jobb.agent_code)) / jobb.revised_weight
        job_list = sorted(job_list, key=operator.attrgetter("revised_process_time"))  # her bir pozisyon için PD
        # değerleri hesaplanan job_list teki işler  "revised_process_time" attributelarına göre sıralanır.
        schedule_by_PD.append(job_list[0])  # en küçük PD değerine sahip iş schedule_by_PD çizelgesine atanır.
        completion_time = job_list[0].completion_time  # schedule_by_PD çizelgesindeki işin tamamlanma zamanı atanan
        # son işin tamamlanma zamanına eşittir.
        del job_list[0]  # schedule_by_PD çizelgesine atanan iş job_listten silinir.
        _ = + 1
    return schedule_by_PD


def compose_schedule_A_best(job_list, schedule, completion_time, learning_rate, deterioration_rate, interpolation_rate):
    # A ve B ajanına ait işlerden oluşan schedule iş listesi, B ajanına ait hiç bir iş tardy olmaycak şekilde A ajanına
    # ait toplam ağırlıklı tamamlanma zamanının minimize edecek şekilde dal-snır algoritmasına girdi teşkiş etmesi için
    # sıralanır
    """
    :param job_list: çizelgelenecek işler listesi
    :param schedule: fonksiyon tamamlandıktan sonra elde edilecek çizelgenin ekleneceği çizelge
    :param completion_time: scheduledaki son işin tamamlanma zamanı
    :param learning_rate: öğreneme katsayısı
    :param deterioration_rate: bozulma katsayısı
    :param interpolation_rate: interolasyon katsayısı
    :return: initial_schedule: A ajanının amaç fonksiyunu en aza indirgeyecek işler sıralaması
    """
    for job in job_list:
        job.position = 0
        job.completion_time = 0.0
        job.positioned_process_time = 0.0
        job.revised_process_time = 0.0
        job.tardy = 0
    compltion_time = completion_time  # initial solution tamamlanma zamanının gösterir.
    if schedule == 0:
        position = 0
        # print(" A AJANI İÇİN EN İYİ SONUCU VERECEK BAŞLANGIÇ ÇÖZÜM OLUŞTURULACAKTIR.")
    else:
        position = len(schedule)
        # print(" A ajanına ait işler, B ajanına ait işlerden oluşan çizelgenin sonuna atanacaktır")
    initial_schedule = []
    for j in range(0, len(job_list)):
        j = j + position
        # print("Çizelgede {}. poziyona hangi işin atanacağına karar verilecektir.".format(j + 1))
        check_tardiness = []  # initial_solutiona (j+1). pozisyona yeni bir atanırken atanacak iş ve tardy durumuna
        # düşmemesi gereken işler olan B ajanına ait işlerin  birleşiminden oluşur. Tardy duruma düşülüp düşülmediği
        # bu listedeki işlerin pozisyon bazlı proses süreleri hesaplanarak belirlenir.

        unassigned_jobs = [jobb for jobb in job_list if jobb not in initial_schedule]  # başlangıç çözüm çizelgesine
        # atanmamış iş listesini vermektedir.
        # print(" çizelgeye henüz atanmamış A ajanına ait işler {}".format(unassigned_jobs))
        unassigned_jobs = calculate_job_PD(unassigned_jobs, j + 1, compltion_time, learning_rate, deterioration_rate,
                                           interpolation_rate)  # j+1. pozisyon için en küçük PD değerine sahip iş
        # unassigned_jobs listesinin ilk sırasına alınmaktadır.
        # print("  yeni çizelge {}".format(unassigned_jobs))
        unassigned_no_tardy_jobs = [jobb for jobb in unassigned_jobs if jobb.agent_name == "B"]
        unassigned_no_tardy_jobs = sorted(unassigned_no_tardy_jobs, key=operator.attrgetter("deadline"))  # başlangıç
        # çizelgeye atanmamış tardy durumuna düşmemesi gereken B ajanına ait işler deadline larına göre sıralanır.
        number_of_tardy_jobs = 0  # tardy duruma düşmüş iş sayısını göstermektedir.

        if len(unassigned_no_tardy_jobs) == 0:  # şayet tardy olmaması gereken iş kalmamışsa atanmamış işler WPT
            # sistematiğine göre sıralanmış demektir. Her iki ajanın amacı, işlerin PD değerlerine göre sıralaması
            # ile optimize edilebilir.
            initial_schedule.append(unassigned_jobs[0])
            initial_schedule[j].positioned_process_time = \
                calculate_positioned_process_time(initial_schedule[j], (j + 1), compltion_time, learning_rate,
                                                  deterioration_rate)
            initial_schedule[j].completion_time = compltion_time + initial_schedule[j].positioned_process_time
            compltion_time = initial_schedule[j].completion_time

        else:

            if unassigned_jobs[0] in unassigned_no_tardy_jobs:
                # print(" {}. pozisyona atanıp atanmayacağına karar verilecek {} isimli iş, aynı zamanda B ajanı işlerinden biridir.".format((j + 1), unassigned_jobs[0]))
                unassigned_no_tardy_jobs.remove(unassigned_jobs[0])  # check_tardy listesinde mükerrerlik yaşanmaması
                # için bu işlem yapılmaktadır.
            else:
                print("")
                # print(" {}. pozisyona atanıp atanmayacağına karar verilecek {} isimli iş, B ajanı işlerinden biri değildir.".format((j + 1), unassigned_jobs[0]))
            check_tardiness = [unassigned_jobs[0]] + unassigned_no_tardy_jobs
            compltion_time2 = compltion_time
            # print(" {} işi atandığında tardy durum değerlendirilmesi yapılması gereken işler: ".format(check_tardiness[0].name))

            for i in range(0, len(check_tardiness)):
                # print(" {} işiyle ilgili bilgiler:".format(check_tardiness[i].name))
                # print("     proses süresi: {}".format(check_tardiness[i].process_time))
                # print("     deadline: {}".format(check_tardiness[i].deadline))
                # print("     Kendinden önceki işlerin tamamlanma zamanı: {}".format(compltion_time2))
                calculate_positioned_process_time(check_tardiness[i], (i + j + 1), compltion_time2, learning_rate,
                                                  deterioration_rate)
                check_tardiness[i].completion_time = compltion_time2 + check_tardiness[i].positioned_process_time
                # print("     Pozisyon bazlı proses süresi: {}".format(check_tardiness[i].positioned_process_time))
                # print("     İş atandığı durumda yeni tamamlanma zamanı: {}".format(check_tardiness[i].completion_time))
                if (check_tardiness[i].completion_time > check_tardiness[i].deadline) and \
                        (check_tardiness[i].agent_code == 1):  # eğer işin tamamlanma zamanı deadlinedan büyük olursa
                    # tardy duruma düşecektir.
                    check_tardiness[i].tardy = 1
                    check_tardiness[i].tardy_days = check_tardiness[i].completion_time - check_tardiness[i].deadline
                    number_of_tardy_jobs = +1
                    # print("     {}, {}. pozisyona atandığında {} isimli iş geç kalmaması gerekirken geç kalmaktadır".format(check_tardiness[0].name, (j + 1), check_tardiness[i].name))
                    break
                elif (check_tardiness[i].completion_time > check_tardiness[i].deadline) and \
                        (check_tardiness[i].agent_code == 0):
                    check_tardiness[i].tardy = 1
                    check_tardiness[i].tardy_days = check_tardiness[i].completion_time - check_tardiness[i].deadline
                    # print("     {}, {}. pozisyona atandığında {} isimli geç kalması önemli olmayan iş geç kalmaktadır.".format(check_tardiness[0].name, (j + 1), check_tardiness[i].name))
                else:
                    check_tardiness[i].tardy = 0
                    check_tardiness[i].tardy_days = 0
                    # print("     {} işi {}. pozisyona atandığında {} işi geç kalmamaktadır.".format(check_tardiness[0].name, (j + 1), check_tardiness[i].name))
                compltion_time2 = check_tardiness[i].completion_time
                i = +1

            if number_of_tardy_jobs == 0:
                # print("  {} işi başlangıç çözümüne eklenecektir.".format(check_tardiness[0]))
                initial_schedule.append(check_tardiness[0])
                # print("  Başlangıç çözümdeki işler:")
                # for jobb in initial_schedule:
                    # print("     {} -> ".format(jobb.name))
                compltion_time = check_tardiness[0].completion_time
                # print(" Yeni tamamlanma zamanı {} olmuştur.".format(compltion_time))
            elif (number_of_tardy_jobs > 0) and (check_tardiness[0].completion_time > check_tardiness[0].deadline) and \
                    (check_tardiness[0].agent_code == 1):
                print("")
                # print(" Çözüm INFEASIBLE dır")
            else:
                # print(" {} atandığında tardy durumuna düşmemesi gereken işler geç kaldığından, atanacaklar listesinden çıkarılmıştır.".format(check_tardiness[0].name))
                check_tardiness = unassigned_no_tardy_jobs
                # print(" Yeni atanabilecek işler sadece tardy durumuna düşmemesi gereken işlerdir:")
                # for jobb in check_tardiness:
                   # print("     {} -> ".format(jobb.name))
                completion_time4 = compltion_time
                number_of_tardy_jobs2 = 0
                # print(" {} işi atandığında tardy durum değerlendirilmesi yapılması gereken işler: ".format(check_tardiness[0].name))
                for i in range(0, len(check_tardiness)):
                    # print("     {} işiyle ilgili bilgiler:".format(check_tardiness[i].name))
                    # print("     proses süresi: {}".format(check_tardiness[i].process_time))
                    # print("     deadline: {}".format(check_tardiness[i].deadline))
                    # print("     Kendinden önceki işlerin tamamlanma zamanı: {}".format(completion_time4))
                    calculate_positioned_process_time(check_tardiness[i], (i + j + 1), completion_time4, learning_rate,
                                                      deterioration_rate)
                    check_tardiness[i].completion_time = completion_time4 + check_tardiness[i].positioned_process_time
                    # print("     Pozisyon bazlı proses süresi: {}".format(check_tardiness[i].positioned_process_time))
                    # print("     İş atandığı durumda yeni tamamlanma zamanı: {}".format(check_tardiness[i].completion_time))
                    if check_tardiness[i].completion_time > check_tardiness[i].deadline:
                        check_tardiness[i].tardy = 1
                        check_tardiness[i].tardy_days = check_tardiness[i].completion_time - check_tardiness[i].deadline
                        number_of_tardy_jobs2 = +1
                        # print("     Tardy durumuna düşmektedir".format(check_tardiness[i].name))
                        break
                    else:
                        check_tardiness[i].tardy = 0
                        check_tardiness[i].tardy_days = 0
                        # print("     {} işi {}. pozisyona atandığında {} işi tardy duruma düşmemektedir.".format(check_tardiness[0].name, (j + 1), check_tardiness[i].name))
                    completion_time4 = check_tardiness[i].completion_time
                    i = +1
                if number_of_tardy_jobs2 == 0:
                    # print("     {} işi başlangıç çözümüne eklenecektir.".format(check_tardiness[0]))
                    initial_schedule.append(check_tardiness[0])
                    # print("     Başlangıç çözümdeki işler:")
                    # for jobb in initial_schedule:
                        # print("     {} -> ".format(jobb.name))
                    compltion_time = check_tardiness[0].completion_time
                else:
                    print("")
                    # print("Çözüm infeasibledır.")
                    break

        if j == len(job_list) - 1:
            for jobb in initial_schedule:
                print("{}. {} -> gerçek proses süresi: {} -> yeni proses süresi: {} -> tamamlanma: {} -> "
                      "deadline: {} -> weight: {}" .format(jobb.position, jobb.name, jobb.process_time,
                                                           jobb.positioned_process_time, jobb.completion_time,
                                                           jobb.deadline, jobb.weight))
        print("")
        #  j = +1
    return initial_schedule


def compose_schedule_all_agents(schedule, a_best, b_best, a_worst, b_worst, learning_rate, deterioration_rate):
    """
    :param schedule:
    :param a_best:
    :param b_best:
    :param a_worst:
    :param b_worst:
    :param learning_rate:
    :param deterioration_rate:
    :return:
    """
    for job in schedule:
        job.position = 0
        job.completion_time = 0.0
        job.positioned_process_time = 0.0
        job.revised_process_time = 0.0
        job.tardy = 0

    initial_schedule = []  # fonksiyon sonucu elde edilecek iş listesini göstermektedir.
    compltion_time = 0.0  # initial solution tamamlanma zamanının gösterir.
    for j in range(0, len(schedule)):
        # print("Çizelgede {}. poziyona hangi işin atanacağına karar verilecektir.".format(j + 1))
        check_tardiness = []  # initial_solutiona (j+1). pozisyona yeni bir atanırken atanacak iş ve tardy durumuna
        unassigned_jobs = [jobb for jobb in schedule if jobb not in initial_schedule]  # başlangıç çözüm çizelgesine
        # atanmamış iş listesini vermektedir.
        unassigned_jobs = calculate_schedule_by_PD_all_agents_adjusted_weights(unassigned_jobs, j + 1, compltion_time,
                                                                               a_best, b_best, a_worst, b_worst,
                                                                               learning_rate, deterioration_rate)
        # j+1. pozisyon için en küçük PD değerine sahip iş unassigned_jobs listesinin ilk sırasına alınmaktadır.
        unassigned_no_tardy_jobs = [jobb for jobb in unassigned_jobs if jobb.agent_name == "B"]
        unassigned_no_tardy_jobs = sorted(unassigned_no_tardy_jobs, key=operator.attrgetter("deadline"))  # başlangıç
        # çizelgeye atanmamış tardy durumuna düşmemesi gereken B ajanına ait işler deadline larına göre sıralanır.
        number_of_tardy_jobs = 0  # tardy duruma düşmüş iş sayısını göstermektedir.

        if len(unassigned_no_tardy_jobs) == 0:  # şayet tardy olmaması gereken iş kalmamışsa atanmamış işler WPT
            initial_schedule.append(unassigned_jobs[0])
            initial_schedule[j].positioned_process_time = \
                calculate_positioned_process_time(initial_schedule[j], (j + 1), compltion_time, learning_rate,
                                                  deterioration_rate)
            initial_schedule[j].completion_time = compltion_time + initial_schedule[j].positioned_process_time
            compltion_time = initial_schedule[j].completion_time
        else:
            print("")
            if unassigned_jobs[0] in unassigned_no_tardy_jobs:
                # print(" {}. pozisyona atanıp atanmayacağına karar verilecek {} isimli iş, aynı zamanda B ajanı işlerinden biridir.".format((j + 1), unassigned_jobs[0]))
                unassigned_no_tardy_jobs.remove(unassigned_jobs[0])  # check_tardy listesinde mükerrerlik yaşanmaması
                # için bu işlem yapılmaktadır.
            else:
                print("")
                # print(" {}. pozisyona atanıp atanmayacağına karar verilecek {} isimli iş, B ajanı işlerinden biri değildir.".format((j + 1), unassigned_jobs[0]))
            check_tardiness = [unassigned_jobs[0]] + unassigned_no_tardy_jobs
            compltion_time2 = compltion_time
            # print(" {} işi atandığında tardy durum değerlendirilmesi yapılması gereken işler: ". format(check_tardiness[0].name))

            for i in range(0, len(check_tardiness)):
                calculate_positioned_process_time(check_tardiness[i], (i + j + 1), compltion_time2, learning_rate,
                                                  deterioration_rate)
                check_tardiness[i].completion_time = compltion_time2 + check_tardiness[i].positioned_process_time
                # print("     Pozisyon bazlı proses süresi: {}".format(check_tardiness[i].positioned_process_time))
                # print("     İş atandığı durumda yeni tamamlanma zamanı: {}".format(check_tardiness[i].completion_time))
                if (check_tardiness[i].completion_time > check_tardiness[i].deadline) and \
                        (check_tardiness[i].agent_code == 1):  # eğer işin tamamlanma zamanı deadlinedan büyük olursa
                    # tardy duruma düşecektir.
                    check_tardiness[i].tardy = 1
                    check_tardiness[i].tardy_days = check_tardiness[i].completion_time - check_tardiness[i].deadline
                    number_of_tardy_jobs = +1
                    # print("     {}, {}. pozisyona atandığında {} isimli iş geç kalmaması gerekirken geç kalmaktadır". format(check_tardiness[0].name, (j + 1), check_tardiness[i].name))
                    break
                elif (check_tardiness[i].completion_time > check_tardiness[i].deadline) and \
                        (check_tardiness[i].agent_code == 0):
                    check_tardiness[i].tardy = 1
                    check_tardiness[i].tardy_days = check_tardiness[i].completion_time - check_tardiness[i].deadline
                    # print("     {}, {}. pozisyona atandığında {} isimli geç kalması önemli olmayan iş geç kalmaktadır.".format(check_tardiness[0].name, (j + 1), check_tardiness[i].name))
                else:
                    check_tardiness[i].tardy = 0
                    check_tardiness[i].tardy_days = 0
                    # print("     {} işi {}. pozisyona atandığında {} işi geç kalmamaktadır.". format(check_tardiness[0].name, (j + 1), check_tardiness[i].name))
                compltion_time2 = check_tardiness[i].completion_time
                i = +1
            if number_of_tardy_jobs == 0:
                # print("  {} işi başlangıç çözümüne eklenecektir.".format(check_tardiness[0]))
                initial_schedule.append(check_tardiness[0])
                # print("  Başlangıç çözümdeki işler:")
                # for jobb in initial_schedule:
                    # print("     {} -> ".format(jobb.name))
                compltion_time = check_tardiness[0].completion_time
                # print(" Yeni tamamlanma zamanı {} olmuştur.".format(compltion_time))
            elif (number_of_tardy_jobs > 0) and (check_tardiness[0].completion_time > check_tardiness[0].deadline) and \
                    (check_tardiness[0].agent_code == 1):
                print("")
                # print(" Çözüm INFEASIBLE dır")
            else:
                # print(" {} atandığında tardy durumuna düşmemesi gereken işler geç kaldığından, atanacaklar listesinden çıkarılmıştır.".format(check_tardiness[0].name))
                check_tardiness = unassigned_no_tardy_jobs
                # print(" Yeni atanabilecek işler sadece tardy durumuna düşmemesi gereken işlerdir:")
                # for jobb in check_tardiness:
                    # print("     {} -> ".format(jobb.name))
                completion_time4 = compltion_time
                number_of_tardy_jobs2 = 0
                # print(" {} işi atandığında tardy durum değerlendirilmesi yapılması gereken işler: ".format(check_tardiness[0].name))
                for i in range(0, len(check_tardiness)):
                    calculate_positioned_process_time(check_tardiness[i], (i + j + 1), completion_time4, learning_rate,
                                                      deterioration_rate)
                    check_tardiness[i].completion_time = completion_time4 + check_tardiness[i].positioned_process_time
                    # print("     Pozisyon bazlı proses süresi: {}".format(check_tardiness[i].positioned_process_time))
                    # print("     İş atandığı durumda yeni tamamlanma zamanı: {}".format(check_tardiness[i].completion_time))
                    if check_tardiness[i].completion_time > check_tardiness[i].deadline:
                        check_tardiness[i].tardy = 1
                        check_tardiness[i].tardy_days = check_tardiness[i].completion_time - check_tardiness[i].deadline
                        number_of_tardy_jobs2 = +1
                        # print("     Tardy durumuna düşmektedir".format(check_tardiness[i].name))
                        break
                    else:
                        check_tardiness[i].tardy = 0
                        check_tardiness[i].tardy_days = 0
                        # print("     {} işi {}. pozisyona atandığında {} işi tardy duruma düşmemektedir.".format(check_tardiness[0].name, (j + 1), check_tardiness[i].name))
                    completion_time4 = check_tardiness[i].completion_time
                    i = +1
                if number_of_tardy_jobs2 == 0:
                    # print("     {} işi başlangıç çözümüne eklenecektir.".format(check_tardiness[0]))
                    initial_schedule.append(check_tardiness[0])
                    # print("     Başlangıç çözümdeki işler:")
                    # for jobb in initial_schedule:
                        # print("     {} -> ".format(jobb.name))
                    compltion_time = check_tardiness[0].completion_time
                else:
                    print("")
                    # print("Çözüm infeasibledır.")
                    break
        if j == len(schedule) - 1:
            for jobb in initial_schedule:
                print("{}. {} -> gerçek proses süresi: {} -> yeni proses süresi: {} -> tamamlanma: {} -> deadline: {} "
                      "-> weight: {}" .format(jobb.position, jobb.name, jobb.process_time, jobb.positioned_process_time,
                                              jobb.completion_time, jobb.deadline, jobb.weight))
        print("")
        j = +1
    return initial_schedule


def compose_schedule_B_best(job_list, schedule, completion_time, learning_rate, deterioration_rate):
    """
       :param job_list: çizelgelenecek işler listesi
       :param schedule: fonksiyon tamamlandıktan sonra elde edilecek çizelgenin ekleneceği çizelge
       :param completion_time: scheduledaki son işin tamamlanma zamanı
       :param learning_rate: öğreneme katsayısı
       :param deterioration_rate: bozulma katsayısı
       :return: initial_schedule: A ajanının amaç fonksiyunu en aza indirgeyecek işler sıralaması
       """
    # job_listi alarak öğrenme (learning_rate) ve bozulma (deterioration_rate) etkileri altında;
    # B ajanına ait işler tardy duruma düşmeyecek şekilde yeniden sıralar.

    compltion_time = completion_time
    if schedule == 0:
        position = 0
        # print(" B AJANI İÇİN EN İYİ SONUCU VERECEK BAŞLANGIÇ ÇÖZÜM OLUŞTURULACAKTIR.")
    else:
        # print("node a ait son işin tamamlanma zamanı ", compltion_time )
        position = len(schedule)
        # print(" B ajanına ait işler, A ajanına ait işlerden oluşan çizelgenin sonuna atanacaktır")

    initial_schedule = []  # fonksiyon sonucu elde edilecek iş listesini göstermektedir.
    A_agent_jobs = [jobb for jobb in job_list if jobb.agent_name == "A"]
    job_list = [jobb for jobb in job_list if jobb.agent_name == "B"]
    for j in range(0, len(job_list)):
        j = j + position
        # print("Çizelgede {}. poziyona hangi işin atanacağına karar verilecektir.".format(j + 1))
        check_tardiness = []  # initial_solutiona (j+1). pozisyona yeni bir atanırken atanacak iş ve tardy durumuna
        # düşmemesi gereken işler olan B ajanına ait işlerin  birleşiminden oluşur. Tardy duruma düşülüp düşülmediği
        # bu listedeki işlerin pozisyon bazlı proses süreleri hesaplanarak belirlenir.
        unassigned_jobs = [jobb for jobb in job_list if jobb not in initial_schedule]  # başlangıç çözüm çizelgesine
        # atanmamış iş listesini vermektedir.
        # print(" çizelgeye henüz atanmamış B ajanına ait işler {}".format(unassigned_jobs))
        unassigned_jobs = calculate_schedule_by_PD_all_agents(unassigned_jobs, j + 1, compltion_time, learning_rate,
                                                              deterioration_rate)
        # print("  yeni çizelge {}".format(unassigned_jobs))

        unassigned_jobs2 = unassigned_jobs.copy()
        unassigned_jobs2.pop(0)
        unassigned_jobs2 = sorted(unassigned_jobs2, key=operator.attrgetter("deadline"))  # başlangıç
        # çizelgeye atanmamış tardy durumuna düşmemesi gereken  işler deadline larına göre sıralanır.
        number_of_tardy_jobs = 0  # tardy duruma düşmüş iş sayısını göstermektedir.
        check_tardiness.append(unassigned_jobs[0])
        check_tardiness = check_tardiness + unassigned_jobs2
        compltion_time2 = compltion_time
        # print(" {} işi atandığında tardy durum değerlendirilmesi yapılması gereken işler: ".format(check_tardiness[0].name))
        for i in range(0, len(check_tardiness)):
            calculate_positioned_process_time(check_tardiness[i], (i + j + 1), compltion_time2, learning_rate,
                                              deterioration_rate)
            check_tardiness[i].completion_time = compltion_time2 + check_tardiness[i].positioned_process_time
            # print("     Pozisyon bazlı proses süresi: {}".format(check_tardiness[i].positioned_process_time))
            # print("     İş atandığı durumda yeni tamamlanma zamanı: {}".format(check_tardiness[i].completion_time))
            if check_tardiness[i].completion_time > check_tardiness[i].deadline:
                # eğer işin tamamlanma zamanı deadlinedan büyük olursa tardy duruma düşecektir.
                check_tardiness[i].tardy = 1
                check_tardiness[i].tardy_days = check_tardiness[i].completion_time - check_tardiness[i].deadline
                number_of_tardy_jobs = +1
                # print("     {}, {}. pozisyona atandığında {} isimli iş geç kalmaması gerekirken geç kalmaktadır".format(check_tardiness[0].name, (j + 1), check_tardiness[i].name))
                break
            else:
                check_tardiness[i].tardy = 0
                check_tardiness[i].tardy_days = 0
                # print("     {} işi {}. pozisyona atandığında {} işi geç kalmamaktadır.".format(check_tardiness[0].name, (j + 1), check_tardiness[i].name))
            compltion_time2 = check_tardiness[i].completion_time
            i = +1
        if number_of_tardy_jobs == 0:
            # print("  {} işi başlangıç çözümüne eklenecektir.".format(check_tardiness[0]))
            initial_schedule.append(check_tardiness[0])
            # print("  Başlangıç çözümdeki işler:")
            # for jobb in initial_schedule:
                # print("     {} -> ".format(jobb.name))
            compltion_time = check_tardiness[0].completion_time
            # print(" Yeni tamamlanma zamanı {} olmuştur.".format(compltion_time))
        else:
            # print(" {} atandığında tardy durumuna düşmemesi gereken işler geç kaldığından, atanacaklar listesinden çıkarılmıştır.".format(check_tardiness[0].name))
            check_tardiness = sorted(check_tardiness, key=operator.attrgetter("deadline"))
            completion_time4 = compltion_time
            number_of_tardy_jobs2 = 0
            # print(" {} işi atandığında tardy durum değerlendirilmesi yapılması gereken işler: ".format(check_tardiness[0].name))
            for i in range(0, len(check_tardiness)):
                calculate_positioned_process_time(check_tardiness[i], (i + j + 1), completion_time4, learning_rate,
                                                  deterioration_rate)
                check_tardiness[i].completion_time = completion_time4 + check_tardiness[i].positioned_process_time
                if check_tardiness[i].completion_time > check_tardiness[i].deadline:
                    check_tardiness[i].tardy = 1
                    check_tardiness[i].tardy_days = check_tardiness[i].completion_time - check_tardiness[i].deadline
                    number_of_tardy_jobs2 = +1
                    # print("     Tardy durumuna düşmektedir".format(check_tardiness[i].name))
                    break
                else:
                    check_tardiness[i].tardy = 0
                    check_tardiness[i].tardy_days = 0
                    # print("     {} işi {}. pozisyona atandığında {} işi tardy duruma düşmemektedir.".format(check_tardiness[0].name, (j + 1), check_tardiness[i].name))
                completion_time4 = check_tardiness[i].completion_time
                i = +1
            if number_of_tardy_jobs2 == 0:
                # print("     {} işi başlangıç çözümüne eklenecektir.".format(check_tardiness[0]))
                initial_schedule.append(check_tardiness[0])
                # print("     Başlangıç çözümdeki işler:")
                # for jobb in initial_schedule:
                    # print("     {} -> ".format(jobb.name))
                compltion_time = check_tardiness[0].completion_time
            else:
                print("")
                # print("Çözüm infeasibledır.")
                break
        j = +1

    if len(A_agent_jobs) > 0:
        A_agent_jobs = calculate_schedule_by_PD_all_agents(A_agent_jobs, len(job_list) + 1,
                                                           initial_schedule[-1].completion_time, learning_rate,
                                                           deterioration_rate)
        # print(A_agent_jobs)
    initial_schedule = initial_schedule + A_agent_jobs
    # print("A ajanına ait işler çizelgeye atandıktan sonra çizelge son durum:")
    for jobb in initial_schedule:
        print("     {}. {} -> gerçek proses süresi: {} -> yeni proses süresi: {} -> tamamlanma: {} -> deadline: {} -> weight: {}".format(jobb.position, jobb.name, jobb.process_time, jobb.positioned_process_time, jobb.completion_time,  jobb.deadline, jobb.weight))
    return initial_schedule


def calculate_object(schedule):
    # verilen çizelgede A ajanı için amaç fonksiyonunu hesaplar
    """
    :param schedule: amaç fonksiyon değeri hesaplanacak çizelge
    :return: amaç dictionary
    """
    object1 = 0.0  # A ajanı amaç fonksiyonu değeri
    object2 = 0.0  # B ajanının amaç fonksiyonu
    if len(schedule) > 0:
        # print("Bu çizelge için:")
        for jobb in schedule:
            object1 = object1 + jobb.completion_time * jobb.weight * (1 - jobb.agent_code)  # toplam ağırlıklı
            # tamamlanma zamanı
            object2 = object2 + jobb.completion_time * jobb.weight * jobb.agent_code
        # print("     A amacı: {}".format(object1))
        # print("     B amacı: {}".format(object2))
    amac = {"A amacı": object1, "B amacı": object2}
    return amac


def node_tardy_check(jobb, node, B_agents_jobs_notassigned, learning_rate, deterioration_rate):
    # node a obb işi atanması söz konusu olduğunda henüz atanmamış B ajanına ait işlerin geç kalıp kalmadığını hesaplar.
    """
    :param jobb: düğüme atanacak iş
    :param node: düğüm
    :param B_agents_jobs_notassigned: düğüme atanmamış B ajanına ait işler
    :param learning_rate: öğreneme katsayısı
    :param deterioration_rate: bozulma katsayısı
    :return: no_of_tardy_job: tardy iş sayısı
    """
    no_of_tardy_job = 0  # tardy durumdaki iş sayısını vermektedir.
    if jobb in B_agents_jobs_notassigned:
        B_agents_jobs_notassigned.remove(jobb)
        if jobb.completion_time > jobb.deadline:
            no_of_tardy_job = 1
    completion_time = jobb.completion_time
    if len(B_agents_jobs_notassigned) > 0:
        for _ in range(0, len(B_agents_jobs_notassigned)):
            position = len(node) + 2 + _
            B_agents_jobs_notassigned[_].positioned_process_time = calculate_positioned_process_time(
                B_agents_jobs_notassigned[_], position, completion_time, learning_rate, deterioration_rate)
            B_agents_jobs_notassigned[_].completion_time = \
                completion_time + B_agents_jobs_notassigned[_].positioned_process_time
            completion_time = B_agents_jobs_notassigned[_].completion_time
            print("         {} işi nodea atandığında node tamamlanma zamanı: {}".format(B_agents_jobs_notassigned[_].name, B_agents_jobs_notassigned[_].completion_time))
            if B_agents_jobs_notassigned[_].completion_time > B_agents_jobs_notassigned[_].deadline:
                print("         B ajanına ait işlerde tardy durumu ortaya çıkmaktadır.")
                no_of_tardy_job = + 1
                break
            _ = + 1
    return no_of_tardy_job


def calculate_LB_A_best(node, node_a_amac, jobs_list, complete_time, learning_rate, deterioration_rate):
    jobs = [job for job in jobs_list if job not in node]
    A_jobs = [job for job in jobs if job.agent_name == "A"]
    B_jobs = [job for job in jobs if job.agent_name == "B"]

    completion_time = complete_time  # çizelgedeki son işin tamamlanma zamanını göstermektedir.
    schedule = calculate_schedule_by_PD_all_agents(A_jobs, (len(node) + len(B_jobs) + 1), completion_time,
                                                   learning_rate, deterioration_rate)
    position2 = len(node) + len(B_jobs) + 1
    LB = node_a_amac
    print("LB hesaplanmadan önce amaç fonksiyonu değeri {}".format(node_a_amac))
    print("Nodeda yeni atanan iş ile toplam iş sayısı {}".format(len(node)))
    print("Nodea atanmamış B ajanı iş sayısı {}".format(len(B_jobs)))
    print("LB değeri hesaplaması {}. pozisyondan başlayacaktır".format(position2))

    completion_time2 = complete_time
    for job in schedule:
        job.positioned_process_time = (job.process_time + completion_time2 * deterioration_rate) * (position2 **
                                                                                                 learning_rate)
        job.completion_time = job.positioned_process_time + completion_time2
        completion_time2 = job.completion_time
        position2 = position2 + 1
        LB = LB + job.completion_time * job.weight
    print("Node LB değeri: {}".format(LB))
    return LB


def calculate_LB_B_best(node, node_b_amac, jobs_list, complete_time, learning_rate, deterioration_rate):
    jobs = [job for job in jobs_list if job not in node]
    A_jobs = [job for job in jobs if job.agent_name == "A"]
    B_jobs = [job for job in jobs if job.agent_name == "B"]

    completion_time = complete_time  # çizelgedeki son işin tamamlanma zamanını göstermektedir.
    schedule = calculate_schedule_by_PD_all_agents(B_jobs, (len(node) + len(A_jobs) + 1), completion_time,
                                                   learning_rate, deterioration_rate)
    position2 = len(node) + len(A_jobs) + 1
    LB = node_b_amac
    completion_time2 = complete_time
    for job in schedule:
        job.positioned_process_time = (job.process_time + completion_time2 * deterioration_rate) * (position2 **
                                                                                                 learning_rate)
        job.completion_time = job.positioned_process_time + completion_time2
        completion_time2 = job.completion_time
        position2 = position2 + 1
        LB = LB + job.completion_time * job.weight
    return LB


def calculate_LB_all_agents(aamac, bamac, a_best, b_best, a_worst, b_worst):
    LB = all_amac(aamac, bamac, a_best, b_best, a_worst, b_worst)
    return LB


def branch_and_bounding_A_best(jobs_list, UB, learning_rate, deterioration_rate):
    """
    :param jobs_list: çizelgelenecek işler
    :param UB: a ajanı amaç fonksiyonu için upper limti
    :param learning_rate: öğrenme katsayısı
    :param deterioration_rate: bozulma katsayısı
    :return: solution_dictionary: dal-sınır algoritması performansını ve sonuçlarını dğerlerndiren dictionary
    """
    solution_dictionary = {}  # dal sınırın CVS dosyasına aktarılması gereken verilerini tutan dictionary
    optimal_cozum_listesi = []  # en düşük LB değerine sahip tüm işleri içeren çizelgeleri veren liste
    olasi_cozumler_list = []  # dal-sınır algoritmesıyla tüm işleri içeren düğümlerin tutulduğu liste
    olasi_cozumler_A_sonuc = []  # dal-sınır algoritmesıyla tüm işleri içeren düğümlerin A ajanı amacı tutulduğu liste
    olasi_cozumler_B_sonuc = []  # dal-sınır algoritmesıyla tüm işleri içeren düğümlerin B ajanı amacı tutulduğu liste
    olasi_cozumler_list_isim = []  # dal-sınır algoritmasıyla tüm işleri içeren düğümlerin iş isimleri tutulur
    node_list = [[]]  # nodeların atandığı listeyi gösterir.
    node_A_amac = [0]  # her bir nodeun A amacı fonksiyonunu gösteren listedir
    node_B_amac = [0]  # her bir nodeun A amacı fonksiyonunu gösteren listedir
    node_tamamlanma_list = [0]  # her bir nodeun son işinin tamamlanma zamanını veren liste
    node_list_isim = [[]]  # her bir nodedaki işlerin isimlerini tutan liste
    # print("A AJANI İÇİN DAL SINIR ALGORİTMASINA BAŞLANACAKTIR.")
    # print("Başlangıç çözüm objective değeri: {}".format(UB))
    for _ in range(0, len(jobs_list)):
        sorted_node = [node for node in node_list if len(node) == _]
        # print("Dallanılabilecek node sayısı = {}".format(len(sorted_node)))
        for j in range(0, len(sorted_node)):
            node = sorted_node[j]
            index = node_list.index(node)
            node_tamamlanma = node_tamamlanma_list[index]
            node_a_amac = node_A_amac[index]
            node_b_amac = node_B_amac[index]
            dugumdeki_isler = node_list_isim[index]
            # print(" ")
            print("mevcut nodedaki işler:{} ".format(dugumdeki_isler))
            jobs_unassigned_to_node = [job for job in jobs_list if job not in node]
            for job in jobs_unassigned_to_node:
                jobs_unassigned_to_node2 = jobs_unassigned_to_node.copy()
                dugumde_olmayan_isler = []
                for _ in jobs_unassigned_to_node2:
                    dugumde_olmayan_isler.append(_.name)
                job.completion_time = 0
                job.position = 0
                job.positioned_process_time = 0.0  # işin çizelge sırasına göre öğrnme-bozlma altında process
                # süresini göstermektedir.
                job.revised_process_time = 0.0  # işin belirlenmiş olan sezgisele göre hesaplanmış proses süresi
                job.tardy = 0  # işin tardy durumuna düşüp düşmediğini gösterir. düşmüyorsa 0 düşüyorsa 1 dir.
                A_agents_jobs_unassigned_to_node = [job for job in jobs_unassigned_to_node2 if job.agent_name == "A"]
                B_agents_jobs_unassigned_to_node = [job for job in jobs_unassigned_to_node2 if job.agent_name == "B"]

                print("mevcut nodea atanmamış işler: {}".format(dugumde_olmayan_isler))
                if jobs_unassigned_to_node2 == B_agents_jobs_unassigned_to_node:
                    print("atanacak iş ", job.name)
                    # print(" ")
                    # print("     Node a atanmamış işler sadece B ajanına ait işlerdir.")
                    # print("     A ajanı amaç fonksiyonunda bir değişme olmayacaktır")
                    # print("     B ajanı işleri kendi içlerinde hiç bir iş geç kalmayacak şekilde nodea eklenecektir.")
                    copied_node = node.copy()
                    B_agents_jobs_unassigned_to_node = compose_schedule_B_best(B_agents_jobs_unassigned_to_node,
                                                                               copied_node, node_tamamlanma,
                                                                               learning_rate, deterioration_rate)
                    for jobb in B_agents_jobs_unassigned_to_node:
                        jobb.position = len(copied_node) + 1
                        jobb.positioned_process_time = (jobb.process_time + deterioration_rate * node_tamamlanma) * \
                                                      (jobb.position ** learning_rate)
                        jobb.completion_time = node_tamamlanma + jobb.positioned_process_time
                        node_tamamlanma = jobb.completion_time
                        node_b_amac = node_b_amac + jobb.completion_time * jobb.weight
                        copied_node.append(jobb)

                    copied_node_isim = dugumdeki_isler.copy()
                    copied_node_isim = copied_node_isim + dugumde_olmayan_isler
                    node_list_isim.append(copied_node_isim)
                    node_list.append(copied_node)
                    node_A_amac.append(node_a_amac)
                    node_B_amac.append(node_b_amac)
                    node_tamamlanma_list.append(node_tamamlanma)
                    olasi_cozumler_list.append(copied_node)
                    olasi_cozumler_A_sonuc.append(node_a_amac)
                    olasi_cozumler_B_sonuc.append(node_b_amac)
                    olasi_cozumler_list_isim.append(copied_node_isim)

                    if node_a_amac < UB:
                        UB = node_a_amac
                    # print("--------")
                    break
                elif jobs_unassigned_to_node2 == A_agents_jobs_unassigned_to_node:

                    copied_node = node.copy()
                    print(jobs_unassigned_to_node2)
                    A_agents_jobs_unassigned_to_node = calculate_schedule_by_PD_all_agents(
                        A_agents_jobs_unassigned_to_node, (len(node) + 1), node_tamamlanma, learning_rate,
                        deterioration_rate)

                    print("A_agents_jobs_unassigned_to_node")
                    for jobb in A_agents_jobs_unassigned_to_node:
                        print(jobb.name)
                        jobb.position = len(copied_node) + 1
                        print(jobb.position)
                        jobb.positioned_process_time = ((jobb.process_time + deterioration_rate * node_tamamlanma) *
                                                       (jobb.position ** learning_rate))
                        print(jobb.positioned_process_time)
                        jobb.completion_time = node_tamamlanma + jobb.positioned_process_time
                        print(jobb.completion_time)
                        node_tamamlanma = jobb.completion_time
                        node_a_amac = node_a_amac + jobb.completion_time * jobb.weight
                        copied_node.append(jobb)

                    copied_node_isim = dugumdeki_isler.copy()
                    copied_node_isim = copied_node_isim + dugumde_olmayan_isler
                    completion_time = node_tamamlanma
                    copied_node_a_amac = node_a_amac
                    copied_node_b_amac = node_b_amac
                    print("Yeni amaç fonksiyonu {} olmaktadır".format(copied_node_a_amac))
                    if copied_node_a_amac <= UB:
                        UB = copied_node_a_amac
                        node_list.append(copied_node)
                        node_list_isim.append(copied_node_isim)
                        node_A_amac.append(copied_node_a_amac)
                        node_B_amac.append(copied_node_b_amac)
                        node_tamamlanma_list.append(completion_time)
                        olasi_cozumler_list.append(copied_node)
                        olasi_cozumler_A_sonuc.append(copied_node_a_amac)
                        olasi_cozumler_B_sonuc.append(copied_node_b_amac)
                        olasi_cozumler_list_isim.append(copied_node_isim)

                    else:
                        print("")
                    break
                else:
                    print("{} işi atanacaktır ve bu iş {}{} ajanına aittir".format(job.name, job.agent_name, job.agent_code))
                    print("     İş atanmadan önce  nodeun A ajanı amaç fonksiyon değeri {}".format(node_a_amac))
                    # print("     İş atanmadan önce nodeun B ajanı amaç fonksiyon değeri {}".format(node_b_amac))
                    print("     İş atanmadan önce nodeun son işinin tamamlanma zamanı {}".format(node_tamamlanma))
                    job.positioned_process_time = calculate_positioned_process_time(job, (len(node) + 1),
                                                                                    node_tamamlanma, learning_rate,
                                                                                    deterioration_rate)
                    job.completion_time = job.positioned_process_time + node_tamamlanma
                    copied_node = node.copy()
                    copied_node.append(job)  # düğüme job eklenmiş halini göstermek için kopyalanmıştır.
                    copied_node_isim = dugumdeki_isler.copy()
                    copied_node_isim.append(job.name)
                    copied_node_tamamlanma = job.completion_time
                    copied_node_a_amac = node_a_amac + job.completion_time * job.weight * (1 - job.agent_code)
                    copied_node_b_amac = node_b_amac + job.completion_time * job.weight * job.agent_code
                    node_LB = calculate_LB_A_best(copied_node, copied_node_a_amac, jobs_list, copied_node_tamamlanma,
                                                  learning_rate, deterioration_rate)
                    print("yeni node: {}".format(copied_node_isim))
                    print("     İş atandıktan sonra nodeun A ajanı amaç fonksiyon değeri {}".format(copied_node_a_amac))
                    # print("     İş atandıktan sonra nodeun B ajanı amaç fonksiyon değeri {}".format(copied_node_b_amac))
                    print("     İş atandıktan sonra nodeun tamamlanma zamanı {}".format(copied_node_tamamlanma))
                    print("     İş atandıktan sonra nodeun LB değeri {}".format(node_LB))

                    if node_LB <= UB:
                        print("LB değerinden sonra şimdi de tardy durumuna neden oluyor mu ona bakalım")
                        if job.agent_name == "B" and len(B_agents_jobs_unassigned_to_node) == 1:
                            gec_kalan_is_sayisi = 0
                        else:
                            gec_kalan_is_sayisi = node_tardy_check(job, node, B_agents_jobs_unassigned_to_node,
                                                                   learning_rate, deterioration_rate)
                        if gec_kalan_is_sayisi == 0:
                            print("LB değeri kriterinden sonra tardy kriteri de uygundur. Baskınlık kuralları uygulanacaktır. ")
                            # print("")
                            if len(copied_node) >= 2:
                                copied_node2 = copied_node.copy()
                                copied_node2.remove(copied_node2[-1])
                                copied_node2.remove(copied_node2[-1])
                                copied_node2.append(copied_node[-1])
                                copied_node2.append(copied_node[-2])
                                copied_dugumdeki_isler2 = copied_node_isim.copy()
                                copied_dugumdeki_isler2.remove(copied_dugumdeki_isler2[-1])
                                copied_dugumdeki_isler2.remove(copied_dugumdeki_isler2[-1])
                                copied_dugumdeki_isler2.append(copied_node_isim[-1])
                                copied_dugumdeki_isler2.append(copied_node_isim[-2])
                                print("Baskınlık kuralları için kıyaslanacak çizelgeler:")
                                print("     yeni oluşturulacak node: {}".format(copied_node_isim))
                                print("     node_listte varsa baskınlığı kıyaslanacak node: {}".format(copied_dugumdeki_isler2))
                                if copied_node2 in node_list:
                                    print("     Baskınlığı kıyaslanacak node node_listte mevcuttur")
                                    index2 = node_list.index(copied_node2)
                                    copied_node2_tamamlanma = node_tamamlanma_list[index2]
                                    copied_node2_a_amac = node_A_amac[index2]
                                    print("      Tamamlanma zamanı: {} ve amaç fonksiyonu {}".format(copied_node2_tamamlanma, copied_node2_a_amac))
                                    print("       Yeni oluşturulacak nodeun tamamlanma zamanı: {} ve amaç fonksiyonu {}".format(copied_node_tamamlanma, copied_node_a_amac))
                                    if (copied_node_a_amac < copied_node2_a_amac and
                                        copied_node_tamamlanma <= copied_node2_tamamlanma) or \
                                            (copied_node2_a_amac == copied_node_a_amac and
                                             copied_node_tamamlanma < copied_node2_tamamlanma):
                                        print(" Baskınlık kuralları gereği mevcut node, node-listten çıkarılacak ve yeni node eklenecektir.")
                                        node_list.pop(index2)
                                        node_list_isim.pop(index2)
                                        node_A_amac.pop(index2)
                                        node_B_amac.pop(index2)
                                        node_tamamlanma_list.pop(index2)

                                        node_list.append(copied_node)
                                        node_list_isim.append(copied_node_isim)
                                        node_A_amac.append(copied_node_a_amac)
                                        node_B_amac.append(copied_node_b_amac)
                                        node_tamamlanma_list.append(copied_node_tamamlanma)

                                    elif (copied_node2_a_amac < copied_node_a_amac and
                                          copied_node2_tamamlanma <= copied_node_tamamlanma) or \
                                            (copied_node2_a_amac == copied_node_a_amac and
                                             copied_node2_tamamlanma < copied_node_tamamlanma):
                                        print("")
                                        print("yeni düğüm baskınlık kuralları gereği listeye eklenmeyecektir.")
                         
                                    else:
                                        print("eski node listeden çıkarılmayacak yeni node ise listeye eklenecektir.")
                                        node_list.append(copied_node)
                                        node_list_isim.append(copied_node_isim)
                                        node_A_amac.append(copied_node_a_amac)
                                        node_B_amac.append(copied_node_b_amac)
                                        node_tamamlanma_list.append(copied_node_tamamlanma)
                                     
                                else:
                                    print("     Baskınlığı kıyaslanacak node node_listte mevcuttur değildir")
                                    # print("     Yeni node node-liste eklenecektir.")
                                    node_list.append(copied_node)
                                    node_list_isim.append(copied_node_isim)
                                    node_A_amac.append(copied_node_a_amac)
                                    node_B_amac.append(copied_node_b_amac)
                                    node_tamamlanma_list.append(copied_node_tamamlanma)
                            
                            else:
                                node_list.append(copied_node)
                                node_list_isim.append(copied_node_isim)
                                node_A_amac.append(copied_node_a_amac)
                                node_B_amac.append(copied_node_b_amac)
                                node_tamamlanma_list.append(copied_node_tamamlanma)
                          

                        else:
                            print("")
                            # print("B ajanına ait işler geç kaldığından bu node üzerinden ilerlenmeyecektir.")
                    else:
                        print("")
                        # print("LB değeri mevcut optimalden büyük olduğu için bu node üzerinden ilerlenmeyecektir.")
                    if len(copied_node) == len(jobs_list):
                        olasi_cozumler_list.append(copied_node)
                        olasi_cozumler_A_sonuc.append(copied_node_a_amac)
                        olasi_cozumler_B_sonuc.append(copied_node_b_amac)
                        olasi_cozumler_list_isim.append(copied_node_isim)
                        # print("--------")
                        if copied_node_a_amac < UB:
                            UB = copied_node_a_amac
            j = +1
        # print("***************************************")
        _ = +1


    zip_dugumler = zip(node_list_isim, node_A_amac)  # tüm düğümlere ait değerleri tutar.
    # print("tüm düğümler ve A ajanı amaç fonksiyoları:")
    for tup in zip_dugumler:
        print(tup)

    # if len(olasi_cozumler_list) == 0:
        # print("çözüm feasible değildir")
    else:
        zipped = zip(olasi_cozumler_list_isim, olasi_cozumler_A_sonuc, olasi_cozumler_B_sonuc, olasi_cozumler_list)
        zipped = list(zipped)  # Converting to list
        res = sorted(zipped, key=operator.itemgetter(1))
        # print("LB ye göre sıralanmış liste : ")
        # print(res)
        A_min_amac = res[0][1]
        for tuples in res:
            if tuples[1] == A_min_amac:
                optimal_cozum_listesi.append(tuples)
        # print("LB ye göre seçilmiş liste : ")
        # print(optimal_cozum_listesi)
        optimal_cozum_listesi = sorted(optimal_cozum_listesi, key=operator.itemgetter(2))
        optimal_cozum_listesi2 = []
        B_max_amac = optimal_cozum_listesi[0][2]
        for tuples in optimal_cozum_listesi:
            if tuples[2] == B_max_amac:
                optimal_cozum_listesi2.append(tuples)
        # print("B ajanı amaç fonksiyonuna göre seçilmiş liste : ")
        # print(optimal_cozum_listesi2)

        for tuples in optimal_cozum_listesi2:
            position = 1
            tamamlanma = 0
            for jobb in tuples[3]:
                jobb.position = position
                calculate_positioned_process_time(jobb, position, tamamlanma, learning_rate, deterioration_rate)
                jobb.completion_time = jobb.positioned_process_time + tamamlanma
                tamamlanma = jobb.completion_time
                position = + 1
                # print("     {}. {} -> gerçek proses süresi: {} -> yeni proses süresi: {} -> tamamlanma: {} -> deadline: {} -> weight: {}".format(jobb.position, jobb.name, jobb.process_time, jobb.positioned_process_time, jobb.completion_time, jobb.deadline, jobb.weight))

        node_ratio = ((len(node_list) - 1) / total_node(len(jobs_list))) * 100
        # print("Bu büyüklükteki bir problem için oluşturulması gereken node sayısının % {}sı kadar node oluşturulmuştur.".format(node_ratio))
        solution_dictionary["toplam_node_sayısı"] = len(node_list) - 1
        solution_dictionary["A ajanı amac"] = A_min_amac
        solution_dictionary["B ajanı amac"] = B_max_amac
        solution_dictionary["cizelgeler"] = optimal_cozum_listesi2
        solution_dictionary["node_ratio"] = node_ratio
        # print(solution_dictionary)
        return solution_dictionary


def branch_and_bounding_B_best(job_list, UB, learning_rate, deterioration_rate):
    # B ajanının hiçbir işi geç kalmaması şartıyla, toplam ağırlıklı tamamlanma zamanını minimize eden çizelgeyi
    # veren fonksiyon
    """
    :param job_list: çizelgelenecek iş listesi
    :param UB: amaç fonksyionu için upper limit değeri
    :param learning_rate: öğrenme katsayısı
    :param deterioration_rate: bozulma katsayısı
    :return solution_dictionary: performans ve sonuçları tutan liste
    """
    A_agents_jobs_list = [job for job in job_list if job.agent_name == "A"]
    jobs_list = [job for job in job_list if job.agent_name == "B"]
    solution_dictionary = {}  # dal sınırın CVS dosyasına aktarılması gereken verilerini tutan dictionary
    optimal_cozum_listesi = []  # en düşük LB değerine sahip tüm işleri içeren çizelgeleri veren liste
    olasi_cozumler_list = []  # dal-sınır algoritmesıyla tüm işleri içeren düğümlerin tutulduğu liste
    olasi_cozumler_B_sonuc = []  # dal-sınır algoritmesıyla tüm işleri içeren düğümlerin B ajanı amacı tutulduğu liste
    olasi_cozumler_list_isim = []  # dal-sınır algoritmasıyla tüm işleri içeren düğümlerin iş isimleri tutulur
    olasi_cozumler_tamamlanma = []  # dal-sınır algoritmasıyla tüm işleri içeren düğümdeki son işin tamamlanma zamanı
    node_list = [[]]  # nodeların atandığı listeyi gösterir.
    node_B_amac = [0]  # her bir nodeun A amacı fonksiyonunu gösteren listedir
    node_tamamlanma_list = [0]  # her bir nodeun son işinin tamamlanma zamanını veren liste
    node_list_isim = [[]]  # her bir nodedaki işlerin isimlerini tutan liste
    # print("B AJANI İÇİN DAL SINIR ALGORİTMASINA BAŞLANACAKTIR.")
    # print("Başlangıç çözüm objective değeri: {}".format(UB))
    for _ in range(0, len(jobs_list)):


        sorted_node = [node for node in node_list if len(node) == _]
        # print("Dallanılabilecek node sayısı = {}".format(len(sorted_node)))
        for j in range(0, len(sorted_node)):
            node = sorted_node[j]
            index = node_list.index(node)
            node_tamamlanma = node_tamamlanma_list[index]
            node_b_amac = node_B_amac[index]
            dugumdeki_isler = node_list_isim[index]
            # print("mevcut nodedaki işler:{} ".format(dugumdeki_isler))
            jobs_unassigned_to_node = [job for job in jobs_list if job not in node]
            for job in jobs_unassigned_to_node:
                jobs_unassigned_to_node2 = jobs_unassigned_to_node.copy()
                dugumde_olmayan_isler = []
                for i in jobs_unassigned_to_node2:
                    dugumde_olmayan_isler.append(i.name)
                job.completion_time = 0
                job.position = 0
                job.positioned_process_time = 0.0  # işin çizelge sırasına göre öğrnme-bozlma altında process
                # süresini göstermektedir.
                job.revised_process_time = 0.0  # işin belirlenmiş olan sezgisele göre hesaplanmış proses süresi
                job.tardy = 0  # işin tardy durumuna düşüp düşmediğini gösterir. düşmüyorsa 0 düşüyorsa 1 dir.


                job.positioned_process_time = calculate_positioned_process_time(job, (len(node) + 1), node_tamamlanma,
                                                                                learning_rate, deterioration_rate)
                job.completion_time = job.positioned_process_time + node_tamamlanma
                copied_node = node.copy()
                copied_node.append(job)  # düğüme job eklenmiş halini göstermek için kopyalanmıştır.
                copied_node_isim = dugumdeki_isler.copy()
                copied_node_isim.append(job.name)
                copied_node_tamamlanma = job.completion_time
                copied_node_b_amac = node_b_amac + job.completion_time * job.weight
                # print("yeni node: {}".format(copied_node_isim))
                # print("     İş atandıktan sonra nodeun B ajanı amaç fonksiyon değeri {}".format(copied_node_b_amac))
                # print("     İş atandıktan sonra nodeun tamamlanma zamanı {}".format(copied_node_tamamlanma))
                if copied_node_b_amac <= UB:
                    # print("LB değerinden sonra şimdi de tardy durumuna neden oluyor mu ona bakalım")
                    gec_kalan_is_sayisi = node_tardy_check(job, node, jobs_unassigned_to_node2,
                                                           learning_rate, deterioration_rate)
                    if gec_kalan_is_sayisi == 0:
                        # print("LB değeri kriterinden sonra tardy kriteri de uygundur. Baskınlık kuralları uygulanacaktır. ")
                        # print("")
                        if len(copied_node) >= 2:
                            copied_node2 = copied_node.copy()
                            copied_node2.remove(copied_node2[-1])
                            copied_node2.remove(copied_node2[-1])
                            copied_node2.append(copied_node[-1])
                            copied_node2.append(copied_node[-2])
                            copied_dugumdeki_isler2 = copied_node_isim.copy()
                            copied_dugumdeki_isler2.remove(copied_dugumdeki_isler2[-1])
                            copied_dugumdeki_isler2.remove(copied_dugumdeki_isler2[-1])
                            copied_dugumdeki_isler2.append(copied_node_isim[-1])
                            copied_dugumdeki_isler2.append(copied_node_isim[-2])
                            # print("Baskınlık kuralları için kıyaslanacak çizelgeler:")
                            # print("     yeni oluşturulacak node: {}".format(copied_node_isim))
                            # print("     node_listte varsa baskınlığı kıyaslanacak node: {}".format(copied_dugumdeki_isler2))
                            if copied_node2 in node_list:
                                # print("     Baskınlığı kıyaslanacak node node_listte mevcuttur")
                                index2 = node_list.index(copied_node2)
                                copied_node2_tamamlanma = node_tamamlanma_list[index2]
                                copied_node2_b_amac = node_B_amac[index2]
                                # print("      Tamamlanma zamanı: {} ve amaç fonksiyonu {}".format(copied_node2_tamamlanma, copied_node2_b_amac))
                                # print("       Yeni oluşturulacak nodeun tamamlanma zamanı: {} ve amaç fonksiyonu {}".format(copied_node_tamamlanma, copied_node_b_amac))
                                if (copied_node_b_amac < copied_node2_b_amac and
                                    copied_node_tamamlanma <= copied_node2_tamamlanma) or \
                                        (copied_node2_b_amac == copied_node_b_amac and
                                         copied_node_tamamlanma < copied_node2_tamamlanma):


                                    node_list.pop(index2)
                                    node_list_isim.pop(index2)
                                    node_B_amac.pop(index2)
                                    node_tamamlanma_list.pop(index2)

                                    node_list.append(copied_node)
                                    node_list_isim.append(copied_node_isim)
                                    node_B_amac.append(copied_node_b_amac)
                                    node_tamamlanma_list.append(copied_node_tamamlanma)

                                elif copied_node2_b_amac == copied_node_b_amac and \
                                        copied_node2_tamamlanma == copied_node_tamamlanma:
                                    # print("eski node listeden çıkarılmayacak yeni node ise listeye eklenecektir.")
                                    node_list.append(copied_node)
                                    node_list_isim.append(copied_node_isim)
                                    node_B_amac.append(copied_node_b_amac)
                                    node_tamamlanma_list.append(copied_node_tamamlanma)

                                else:
                                    print("")

                            else:
                                # print("     Baskınlığı kıyaslanacak node node_listte mevcuttur değildir")
                                # print("     Yeni node node-liste eklenecektir.")
                                node_list.append(copied_node)
                                node_list_isim.append(copied_node_isim)
                                node_B_amac.append(copied_node_b_amac)
                                node_tamamlanma_list.append(copied_node_tamamlanma)

                        else:
                            node_list.append(copied_node)
                            node_list_isim.append(copied_node_isim)
                            node_B_amac.append(copied_node_b_amac)
                            node_tamamlanma_list.append(copied_node_tamamlanma)

                    else:
                        print("")
                        # print("B ajanına ait işler geç kaldığından bu node üzerinden ilerlenmeyecektir.")
                else:
                    print("")
                    # print("LB değeri mevcut optimalden büyük olduğu için bu node üzerinden ilerlenmeyecektir.")
                if len(copied_node) == len(jobs_list):
                    olasi_cozumler_list.append(copied_node)
                    olasi_cozumler_list_isim.append(copied_node_isim)
                    olasi_cozumler_B_sonuc.append(copied_node_b_amac)
                    olasi_cozumler_tamamlanma.append(copied_node_tamamlanma)
                    # print("--------")
                    if copied_node_b_amac < UB:
                        UB = copied_node_b_amac
            j = +1
        # print("***************************************")
        _ = +1


    zipped = zip(olasi_cozumler_list_isim, olasi_cozumler_B_sonuc, olasi_cozumler_tamamlanma, olasi_cozumler_list)
    zipped = list(zipped)  # Converting to list
    res = sorted(zipped, key=operator.itemgetter(1))
    # print("LB ye göre sıralanmış liste : ")
    # print(res)
    B_min_amac = res[0][1]
    for tuples in res:
        if tuples[1] == B_min_amac:
            optimal_cozum_listesi.append(tuples)

    optimal_cozum_listesi = sorted(optimal_cozum_listesi, key=operator.itemgetter(2))
    optimal_cozum_listesi2 = []
    min_tamamlanma = optimal_cozum_listesi[0][2]
    for tuples in optimal_cozum_listesi:
        if tuples[2] == min_tamamlanma:
            optimal_cozum_listesi2.append(tuples)

    position = len(jobs_list)+1
    tamamlanma_zamani = min_tamamlanma
    A_amac = 0  # B ajanı amacının en iyi değeri aldığı durumda A ajanı amacının alacağı değer
    for job in A_agents_jobs_list:
        calculate_positioned_process_time(job, position, tamamlanma_zamani, learning_rate, deterioration_rate)
        job.completion_time = job.positioned_process_time + tamamlanma_zamani
        tamamlanma_zamani = job.completion_time
        position = position + 1
        A_amac = A_amac + job.completion_time * job.weight

    for tuples in optimal_cozum_listesi2:
        for job in A_agents_jobs_list:
            tuples[3].append(job)
            tuples[0].append(job.name)


    node_ratio = ((len(node_list) - 1) / total_node(len(job_list))) * 100
    # print("Bu büyüklükteki bir problem için oluşturulması gereken node sayısının % {}sı kadar node oluşturulmuştur.".format(node_ratio))
    solution_dictionary["toplam_node_sayısı"] = len(node_list) - 1
    solution_dictionary["B ajanı amac"] = B_min_amac
    solution_dictionary["A ajanı amac"] = A_amac
    solution_dictionary["cizelgeler"] = optimal_cozum_listesi2
    solution_dictionary["node_ratio"] = node_ratio
    print(solution_dictionary)
    return solution_dictionary


def branch_and_bounding_all_agents(jobs_list, UB, a_best, b_best, a_worst, b_worst, learning_rate, deterioration_rate):
    """
    :param jobs_list: çizelgelenecek iş listesi
    :param UB: genel çizelge için upper bound değeri
    :param a_best: A ajanı en düşük LB değerini aldığında amaç fonksiyonu değeri
    :param b_best: B ajanı en düşük LB değerini aldığında amaç fonksiyonu değeri
    :param a_worst: A ajanı en yüksek LB değerini aldığında amaç fonksiyonu değeri
    :param b_worst: B ajanı en düşük LB değerini aldığında amaç fonksiyonu değeri
    :param learning_rate: öğrenme katsayısı
    :param deterioration_rate: bozulma katsayısı
    :return solution_dictionary: performans ve sonuçları tutan dictionarty
    """

    solution_dictionary = {}  # dal sınırın CVS dosyasına aktarılması gereken verilerini tutan dictionary
    optimal_cozum_listesi = []  # en düşük LB değerine sahip tüm işleri içeren çizelgeleri veren liste
    olasi_cozumler_list = []  # dal-sınır algoritmesıyla tüm işleri içeren düğümlerin tutulduğu liste
    olasi_cozumler_A_sonuc = []  # dal-sınır algoritmesıyla tüm işleri içeren düğümlerin A ajanı amacı tutulduğu liste
    olasi_cozumler_B_sonuc = []  # dal-sınır algoritmesıyla tüm işleri içeren düğümlerin B ajanı amacı tutulduğu liste
    olasi_cozumler_list_isim = []  # dal-sınır algoritmasıyla tüm işleri içeren düğümlerin iş isimleri tutulur
    olasi_cozumler_ALL_sonuc = []
    node_list = [[]]  # nodeların atandığı listeyi gösterir.
    node_A_amac = [0]  # her bir nodeun A amacı fonksiyonunu gösteren listedir
    node_B_amac = [0]  # her bir nodeun A amacı fonksiyonunu gösteren listedir
    node_ALL_amac = [0]  # A ve B ajanlarının amac fonksiyonlarının beraber değerlendirildiği durum
    node_tamamlanma_list = [0]  # her bir nodeun son işinin tamamlanma zamanını veren liste
    node_list_isim = [[]]  # her bir nodedaki işlerin isimlerini tutan liste
    # print("AJAN AMAÇLARI LİNEER KOMBİNASYONLARI DAL SINIR ALGORİTMASINA BAŞLANACAKTIR.")
    # print("Başlangıç çözüm objective değeri: {}".format(UB))
    for t in range(0, len(jobs_list)):

        sorted_node = [node for node in node_list if len(node) == t]
        # print("Dallanılabilecek node sayısı = {}".format(len(sorted_node)))
        for _ in range(0, len(sorted_node)):
            node = sorted_node[_]
            index = node_list.index(node)
            node_tamamlanma = node_tamamlanma_list[index]
            node_a_amac = node_A_amac[index]
            node_b_amac = node_B_amac[index]
            dugumdeki_isler = node_list_isim[index]
            # print(" ")
            # print("mevcut nodedaki işler:{} ".format(dugumdeki_isler))
            jobs_unassigned_to_node = [job for job in jobs_list if job not in node]
            for job in jobs_unassigned_to_node:
                jobs_unassigned_to_node2 = jobs_unassigned_to_node.copy()
                dugumde_olmayan_isler = []
                for _ in jobs_unassigned_to_node2:
                    dugumde_olmayan_isler.append(_.name)
                job.completion_time = 0
                job.position = 0
                job.positioned_process_time = 0.0  # işin çizelge sırasına göre öğrnme-bozlma altında process
                # süresini göstermektedir.
                job.revised_process_time = 0.0  # işin belirlenmiş olan sezgisele göre hesaplanmış proses süresi
                job.tardy = 0  # işin tardy durumuna düşüp düşmediğini gösterir. düşmüyorsa 0 düşüyorsa 1 dir.
                A_agents_jobs_unassigned_to_node = [job for job in jobs_unassigned_to_node2 if job.agent_name == "A"]
                B_agents_jobs_unassigned_to_node = [job for job in jobs_unassigned_to_node2 if job.agent_name == "B"]

                if jobs_unassigned_to_node2 == B_agents_jobs_unassigned_to_node:

                    copied_node = node.copy()
                    B_agents_jobs_unassigned_to_node = compose_schedule_B_best(B_agents_jobs_unassigned_to_node,
                                                                               copied_node, node_tamamlanma,
                                                                               learning_rate, deterioration_rate)


                    for jobb in B_agents_jobs_unassigned_to_node:
                        jobb.position = len(copied_node) + 1
                        jobb.positioned_process_time = ((jobb.process_time + deterioration_rate * node_tamamlanma) *
                                                       (jobb.position ** learning_rate))
                        jobb.completion_time = node_tamamlanma + jobb.positioned_process_time
                        node_tamamlanma = jobb.completion_time
                        node_b_amac = node_b_amac + jobb.completion_time * jobb.weight
                        copied_node.append(jobb)

                    copied_node = copied_node + B_agents_jobs_unassigned_to_node
                    copied_node_isim = dugumdeki_isler.copy()
                    copied_node_isim = copied_node_isim + dugumde_olmayan_isler
                    completion_time = node_tamamlanma
                    copied_node_b_amac = node_b_amac
                    copied_node_a_amac = node_a_amac

                    # print("     B ajanına ait işler atandıktan sonra nodeun A ajanı amaç fonksiyon değeri {}".format(copied_node_a_amac))
                    # print("     B ajanına ait işler atandıktan sonra nodeun B ajanı amaç fonksiyon değeri {}".format(copied_node_b_amac))
                    # print("     B ajanına ait işler atandıktan sonra nodeun son işinin tamamlanma zamanı {}".format(completion_time))
                    node_amac = all_amac(copied_node_a_amac, copied_node_b_amac, a_best, b_best, a_worst, b_worst)
                    # print("yeni node için amac fonksiyonu değeri değeri {}".format(node_amac))
                    if copied_node_b_amac <= b_worst and node_amac <= UB:
                        node_list.append(copied_node)
                        node_list_isim.append(copied_node_isim)
                        node_A_amac.append(node_a_amac)
                        node_B_amac.append(copied_node_b_amac)
                        node_tamamlanma_list.append(completion_time)
                        node_ALL_amac.append(node_amac)
                        olasi_cozumler_list.append(copied_node)
                        olasi_cozumler_A_sonuc.append(node_a_amac)
                        olasi_cozumler_B_sonuc.append(copied_node_b_amac)
                        olasi_cozumler_list_isim.append(copied_node_isim)
                        olasi_cozumler_ALL_sonuc.append(node_amac)


                    if node_amac < UB:
                        UB = node_amac
                    # print("--------")
                    break
                elif jobs_unassigned_to_node2 == A_agents_jobs_unassigned_to_node:
                    # print(" ")
                    # print("Node a atanmamış işler sadece A ajanına ait işlerdir.")
                    # print("Tardy kontrolü yapılmasına gerek yoktur.")
                    # print("A ajanına ait işler PD değerlerine göre node a olduğu gibi eklenebilir.")
                    copied_node = node.copy()
                    A_agents_jobs_unassigned_to_node = \
                        calculate_schedule_by_PD_all_agents(A_agents_jobs_unassigned_to_node, (len(node) + 1),
                                                            node_tamamlanma, learning_rate, deterioration_rate)


                    for jobb in A_agents_jobs_unassigned_to_node:
                        jobb.position = len(copied_node) + 1
                        jobb.positioned_process_time = ((jobb.process_time + deterioration_rate * node_tamamlanma) *
                                                       (jobb.position ** learning_rate))
                        jobb.completion_time = node_tamamlanma + jobb.positioned_process_time
                        node_tamamlanma = jobb.completion_time
                        node_a_amac = node_a_amac + jobb.completion_time * jobb.weight
                        copied_node.append(jobb)

                    copied_node_isim = dugumdeki_isler.copy()
                    copied_node_isim = copied_node_isim + dugumde_olmayan_isler
                    completion_time = node_tamamlanma
                    copied_node_a_amac = node_a_amac
                    copied_node_b_amac = node_b_amac

                    node_amac = all_amac(copied_node_a_amac, copied_node_b_amac, a_best, b_best, a_worst, b_worst)
                    # print("yeni node için hesaplanan A ajanı amacı {}, B ajanı amacı {} dır.".format(copied_node_a_amac, node_b_amac))
                    # print("Yeni amaç fonksiyonu {} olmaktadır".format(node_amac))
                    if copied_node_a_amac <= a_worst and node_amac <= UB:
                        UB = node_amac
                        node_list.append(copied_node)
                        node_list_isim.append(copied_node_isim)
                        node_A_amac.append(copied_node_a_amac)
                        node_B_amac.append(copied_node_b_amac)
                        node_tamamlanma_list.append(completion_time)
                        node_ALL_amac.append(node_amac)
                        olasi_cozumler_list.append(copied_node)
                        olasi_cozumler_A_sonuc.append(copied_node_a_amac)
                        olasi_cozumler_B_sonuc.append(copied_node_b_amac)
                        olasi_cozumler_list_isim.append(copied_node_isim)
                        olasi_cozumler_ALL_sonuc.append(node_amac)

                        if node_amac < UB:
                            UB = node_amac
                        # print("--------")
                    else:
                        print("")

                    break
                else:

                    job.positioned_process_time = calculate_positioned_process_time(job, (len(node) + 1),
                                                                                    node_tamamlanma, learning_rate,
                                                                                    deterioration_rate)
                    job.completion_time = job.positioned_process_time + node_tamamlanma
                    copied_node = node.copy()
                    copied_node.append(job)  # düğüme job eklenmiş halini göstermek için kopyalanmıştır.
                    copied_node_isim = dugumdeki_isler.copy()
                    copied_node_isim.append(job.name)
                    copied_node_tamamlanma = job.completion_time
                    copied_node_a_amac = node_a_amac + job.completion_time * job.weight * (1 - job.agent_code)
                    copied_node_b_amac = node_b_amac + job.completion_time * job.weight * job.agent_code
                    node_amac = all_amac(copied_node_a_amac, copied_node_b_amac, a_best, b_best, a_worst, b_worst)
                    node_LB_A = calculate_LB_A_best(copied_node, copied_node_a_amac, jobs_list, copied_node_tamamlanma,
                                                  learning_rate, deterioration_rate)
                    node_LB_B = calculate_LB_B_best(copied_node, copied_node_b_amac, jobs_list,
                                                    copied_node_tamamlanma, learning_rate, deterioration_rate)
                    node_LB = calculate_LB_all_agents(node_LB_A, node_LB_B, a_best, b_best, a_worst,
                                                      b_worst)

                    if node_LB_A <= a_worst and node_LB_B <= b_worst and node_LB <= UB:
                        # print("LB değerinden sonra şimdi de tardy durumuna neden oluyor mu ona bakalım")
                        if job.agent_name == "B" and len(B_agents_jobs_unassigned_to_node) == 1:
                            gec_kalan_is_sayisi = 0
                        else:
                            gec_kalan_is_sayisi = node_tardy_check(job, node, B_agents_jobs_unassigned_to_node,
                                                                   learning_rate, deterioration_rate)
                        if gec_kalan_is_sayisi == 0:
                            # print("LB değeri kriterinden sonra tardy kriteri de uygundur. Baskınlık kuralları uygulanacaktır. ")
                            # print("")
                            if len(copied_node) >= 2:
                                copied_node2 = copied_node.copy()
                                copied_node2.remove(copied_node2[-1])
                                copied_node2.remove(copied_node2[-1])
                                copied_node2.append(copied_node[-1])
                                copied_node2.append(copied_node[-2])
                                copied_dugumdeki_isler2 = copied_node_isim.copy()
                                copied_dugumdeki_isler2.remove(copied_dugumdeki_isler2[-1])
                                copied_dugumdeki_isler2.remove(copied_dugumdeki_isler2[-1])
                                copied_dugumdeki_isler2.append(copied_node_isim[-1])
                                copied_dugumdeki_isler2.append(copied_node_isim[-2])
                                # print("Baskınlık kuralları için kıyaslanacak çizelgeler:")
                                # print("     yeni oluşturulacak node: {}".format(copied_node_isim))
                                # print("     node_listte varsa baskınlığı kıyaslanacak node: {}".format(copied_dugumdeki_isler2))
                                if copied_node2 in node_list:
                                    # print("     Baskınlığı kıyaslanacak node node_listte mevcuttur")
                                    index2 = node_list.index(copied_node2)
                                    copied_node2_tamamlanma = node_tamamlanma_list[index2]
                                    copied_node2_all_amac = node_ALL_amac[index2]
                                    # print("      Tamamlanma zamanı: {} ve amaç fonksiyonu {}".format(copied_node2_tamamlanma, copied_node2_all_amac))
                                    # print("       Yeni oluşturulacak nodeun tamamlanma zamanı: {} ve amaç fonksiyonu {}".format(copied_node_tamamlanma, node_amac))
                                    # print(" bu düğümün son işin tamamlanma zamanı: {} ve amaç fonksiyonu {}".format(copied_node2_tamamlanma, copied_node2_all_amac))
                                    if (node_amac < copied_node2_all_amac and
                                        copied_node_tamamlanma <= copied_node2_tamamlanma) or \
                                            (copied_node2_all_amac == node_amac and
                                             copied_node_tamamlanma < copied_node2_tamamlanma):

                                        node_list.pop(index2)
                                        node_list_isim.pop(index2)
                                        node_A_amac.pop(index2)
                                        node_B_amac.pop(index2)
                                        node_tamamlanma_list.pop(index2)
                                        node_ALL_amac.pop(index2)

                                        node_list.append(copied_node)
                                        node_list_isim.append(copied_node_isim)
                                        node_A_amac.append(copied_node_a_amac)
                                        node_B_amac.append(copied_node_b_amac)
                                        node_ALL_amac.append(node_amac)
                                        node_tamamlanma_list.append(copied_node_tamamlanma)
  
                                    elif (copied_node2_all_amac < node_amac and
                                          copied_node2_tamamlanma <= copied_node_tamamlanma) or \
                                            (copied_node2_all_amac == node_amac and
                                             copied_node2_tamamlanma < copied_node_tamamlanma):
                                        print("")
                                  
                                    else:
                                        # print("eski node listeden çıkarılmayacak yeni node ise listeye eklenecektir.")
                                        node_list.append(copied_node)
                                        node_list_isim.append(copied_node_isim)
                                        node_A_amac.append(copied_node_a_amac)
                                        node_B_amac.append(copied_node_b_amac)
                                        node_ALL_amac.append(node_amac)
                                        node_tamamlanma_list.append(copied_node_tamamlanma)
  
                                else:
                                    # print("     Baskınlığı kıyaslanacak node node_listte mevcuttur değildir")
                                    # print("     Yeni node node-liste eklenecektir.")
                                    node_list.append(copied_node)
                                    node_list_isim.append(copied_node_isim)
                                    node_A_amac.append(copied_node_a_amac)
                                    node_B_amac.append(copied_node_b_amac)
                                    node_ALL_amac.append(node_amac)
                                    node_tamamlanma_list.append(copied_node_tamamlanma)

                            else:
                                node_list.append(copied_node)
                                node_list_isim.append(copied_node_isim)
                                node_A_amac.append(copied_node_a_amac)
                                node_B_amac.append(copied_node_b_amac)
                                node_ALL_amac.append(node_amac)
                                node_tamamlanma_list.append(copied_node_tamamlanma)

                        else:
                            print("")
                            # print("B ajanına ait işler geç kaldığından bu node üzerinden ilerlenmeyecektir.")
                    else:
                        print("")
                        # print("LB değeri mevcut optimalden büyük olduğu için bu node üzerinden ilerlenmeyecektir.")
                    if len(copied_node) == len(jobs_list):
                        olasi_cozumler_list.append(copied_node)
                        olasi_cozumler_A_sonuc.append(copied_node_a_amac)
                        olasi_cozumler_B_sonuc.append(copied_node_b_amac)
                        olasi_cozumler_ALL_sonuc.append(node_amac)
                        olasi_cozumler_list_isim.append(copied_node_isim)
                        # print("--------")
                        if node_amac < UB:
                            UB = node_amac
            _ = +1
        # print("***************************************")
        t = +1


    zipped = zip(olasi_cozumler_list_isim, olasi_cozumler_ALL_sonuc, olasi_cozumler_A_sonuc, olasi_cozumler_B_sonuc,
                 olasi_cozumler_list)
    zipped = list(zipped)  # Converting to list
    res = sorted(zipped, key=operator.itemgetter(1))
    # print("LB ye göre sıralanmış liste : ")
    # print(res)
    min_amac = res[0][1]
    for tuples in res:
        if tuples[1] == min_amac:
            optimal_cozum_listesi.append(tuples)
    # print("LB ye göre seçilmiş liste : ")
    # print(optimal_cozum_listesi)
    optimal_cozum_listesi2 = []
    for tuples in optimal_cozum_listesi:
        A_bestten_sapma = (tuples[2] - a_best) / (a_worst - a_best)
        B_bestten_sapma = (tuples[3] - b_best) / (b_worst - b_best)
        optimal_cozum_listesi2.append({"çizelge": tuples[0], "A_bestten_sapma": A_bestten_sapma,
                                       "B_bestten_sapma": B_bestten_sapma})

    node_ratio = ((len(node_list) - 1) / total_node(len(jobs_list))) * 100
    # print("Bu büyüklükteki bir problem için oluşturulması gereken node sayısının % {}sı kadar node oluşturulmuştur.".format(node_ratio))
    solution_dictionary["toplam_node_sayısı"] = (len(node_list) - 1)
    solution_dictionary["cizelge amac"] = min_amac
    solution_dictionary["cizelgeler"] = optimal_cozum_listesi2
    solution_dictionary["node_ratio"] = node_ratio
    # print(solution_dictionary)
    return solution_dictionary


def total_node(number):
    # number adet işi olan bir problem için toplam node sayısını verir.
    """
    :param number: iş sayısı
    :return toplam_node: düğüm sayısı
    """
    toplam_node = 0
    yeni_node = 1
    for _ in range(0, number):
        node = number - _
        yeni_node = yeni_node * node
        toplam_node = toplam_node + yeni_node
    return toplam_node


def all_amac(a, b, a_best, b_best, a_worst, b_worst):
    amac = ((a - a_best) / (a_worst - a_best)) + ((b - b_best) / (b_worst - b_best))
    return amac


def functions_all_A_best(jobs, parameters):
    jobs_ratio = job_analyze(jobs)
    interpolation_coefficient = parameters["interpolation_coefficient"]
    deterioratn_rate = parameters["deterioration_rate"]
    learning_percentage = parameters["learning_percentage"]

    learnng_rate = calculate_learning_coefficient(learning_percentage)  # öğrenme katsayısı hesaplanmaktadır.
    schedule_revised = calculate_schedule_by_PD(jobs, 1, 0, learnng_rate, deterioratn_rate,
                                                interpolation_coefficient)

    print("XXXXXXXXXXXXXXXXXXX")

    start_A = time.time()  # A ajanına yönelik en iyi çizelgenin bulunmasına başlama zamanı
    initial_solution_A_best = compose_schedule_A_best(schedule_revised, 0, 0, learnng_rate, deterioratn_rate,
                                                      interpolation_coefficient)  # A ajanının işlerini başlangıç çözüm
    # çizelgenin ilk sıralarına tardy şartlarına dikkat ederek atar.
    print(initial_solution_A_best)
    if len(initial_solution_A_best) == len(jobs):

        initial_solution_A_best_LB = calculate_object(initial_solution_A_best)["A amacı"]
        print("initial_solution_A_best_LB: {}".format(initial_solution_A_best_LB))
        branch_bound_A_best = branch_and_bounding_A_best(initial_solution_A_best, initial_solution_A_best_LB,
                                                         learnng_rate, deterioratn_rate)
        print("A AJANI İÇİN DAL SINIR SONUCU: {}".format(branch_bound_A_best))
        deviation_A_best = (branch_bound_A_best["A ajanı amac"] - initial_solution_A_best_LB) / initial_solution_A_best_LB
        print("dal sınır ie elde edilen sonuç başlangıç çözümden %{} daha iyi sonuç vermiştir.".format(deviation_A_best))
        elapsed_time_A_best = (time.time() - start_A)  # A ajanı en iyi değeri için algoritma süresi
        # 1 birim elapsed_time 1/100 seconda eşdeğerdir.
        #  with open('MAKALE-A-SONUC.csv', mode='w') as csv_file: eğer dosyayı ilk kez oluşturacak olsaydık bunu yazacaktık.
        with open('MAKALE-A-SONUC.csv', mode='a+', newline='') as csv_file:  # Create a writer object from csv module
            fieldnames = ['interpolation coefficient', 'learning rate', 'deterioration rate', 'number_of_A_jobs',
                          'number_of_B_jobs', 'toplam_node_sayısı', 'node_ratio', 'sapma', 'CPU_time',
                          'is_esneklik_medium', 'is_esneklik_max']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            #  writer.writeheader()  # ilk kez oluşturuken eklenecek olan header değerleri
            writer.writerow({'interpolation coefficient': interpolation_coefficient,
                            'learning rate': learning_percentage,
                            'deterioration rate': deterioratn_rate,
                            'number_of_A_jobs': len(A.job_list),
                            'number_of_B_jobs': len(B.job_list),
                            'toplam_node_sayısı': branch_bound_A_best["toplam_node_sayısı"],
                            "node_ratio": branch_bound_A_best["node_ratio"],
                            'sapma': deviation_A_best,
                            'CPU_time': elapsed_time_A_best,
                            'is_esneklik_medium': jobs_ratio["medium"],
                            'is_esneklik_max': jobs_ratio["max"]})
    else:
        print("ÇÖZÜM INFEASİBLE")

""
def functions_all_all_agents(jobs, parameters):
    jobs_ratio = job_analyze(jobs)
    interpolation_coefficient = parameters["interpolation_coefficient"]
    deterioratn_rate = parameters["deterioration_rate"]
    learning_percentage = parameters["learning_percentage"]

    learnng_rate = calculate_learning_coefficient(learning_percentage)  # öğrenme katsayısı hesaplanmaktadır.
    schedule_revised = calculate_schedule_by_PD(jobs, 1, 0, learnng_rate, deterioratn_rate,
                                                interpolation_coefficient)

    start_A = time.time()  # A ajanına yönelik en iyi çizelgenin bulunmasına başlama zamanı

    initial_solution_A_best = compose_schedule_A_best(schedule_revised, 0, 0, learnng_rate, deterioratn_rate,
                                                      interpolation_coefficient)
    print(initial_solution_A_best)
    initial_solution_A_best_A = calculate_object(initial_solution_A_best)["A amacı"]
    initial_solution_A_best_B = calculate_object(initial_solution_A_best)["B amacı"]

    initial_solution_B_best = compose_schedule_B_best(initial_solution_A_best, 0, 0, learnng_rate, deterioratn_rate)
    print(initial_solution_B_best)
    initial_solution_B_best_B = calculate_object(initial_solution_B_best)["B amacı"]
    initial_solution_B_best_A = calculate_object(initial_solution_B_best)["A amacı"]


    if initial_solution_A_best_A < initial_solution_B_best_A:
        A_best = initial_solution_A_best_A
        A_worst = initial_solution_B_best_A
    else:
        A_worst = initial_solution_A_best_A
        A_best = initial_solution_B_best_A
    if initial_solution_B_best_B  < initial_solution_A_best_B:
        B_best = initial_solution_B_best_B
        B_worst = initial_solution_A_best_B
    else:
        B_worst = initial_solution_B_best_B
        B_best = initial_solution_A_best_B

    print("A best: {}, B best {}, A worst {}, B worst {}".format(A_best, B_best, A_worst, B_worst))
    schedule_revised_all_agents = calculate_schedule_by_PD_all_agents_adjusted_weights(jobs, 1, 0, A_best, B_best,
                                                                                       A_worst, B_worst, learnng_rate,
                                                                                       deterioratn_rate)
    initial_solution = compose_schedule_all_agents(schedule_revised_all_agents, A_best, B_best, A_worst, B_worst,
                                                   learnng_rate, deterioratn_rate)
    initial_solution_object = calculate_object(initial_solution)
    if A_best != A_worst and B_best != B_worst:
        lower_bound = all_amac(initial_solution_object["A amacı"], initial_solution_object["B amacı"],
                               A_best, B_best, A_worst, B_worst)
        print(" çizelge A amacı {}  B amacı {} ve lower_bound değeri {}"
              .format(initial_solution_object["A amacı"], initial_solution_object["B amacı"], lower_bound))
        branch_bound_all_agenst = branch_and_bounding_all_agents(initial_solution, lower_bound, A_best, B_best, A_worst,
                                                                 B_worst, learnng_rate, deterioratn_rate)
        deviation_all_agenst = (branch_bound_all_agenst["cizelge amac"] - lower_bound) / lower_bound
    else:
        deviation_all_agenst = 0
        branch_bound_all_agenst = {"toplam_node_sayısı": 0, "node_ratio": 0}

    elapsed_time_all_agents = (time.time() - start_A)
    # with open('MAKALE-ALL-AGENTS.csv', mode='w') as csv_file:
    with open('MAKALEA-ALL-AGENTS.csv', mode='a+', newline='') as csv_file:  # Create a writer object from csv module
        fieldnames = ['interpolation coefficient', 'learning rate', 'deterioration rate',
                      'number_of_A_jobs', 'number_of_B_jobs', 'all_agents_toplam_node_sayısı', 'all_agents_node_ratio',
                      'all_agents_sapma', 'all_agents_CPU_time', 'is_esneklik_medium', 'is_esneklik_max']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        # writer.writeheader()  # ilk kez oluşturuken eklenecek olan header değerleri
        writer.writerow({'interpolation coefficient': interpolation_coefficient,
                         'learning rate': learning_percentage,
                         'deterioration rate': deterioratn_rate,
                         'number_of_A_jobs': len(A.job_list),
                         'number_of_B_jobs': len(B.job_list),
                         'all_agents_toplam_node_sayısı': branch_bound_all_agenst["toplam_node_sayısı"],
                         "all_agents_node_ratio": branch_bound_all_agenst["node_ratio"],
                         'all_agents_sapma': deviation_all_agenst,
                         'all_agents_CPU_time': elapsed_time_all_agents,
                         'is_esneklik_medium': jobs_ratio["medium"],
                         'is_esneklik_max': jobs_ratio["max"]})


def functions_all(jobs, parameters):
    jobs_ratio = job_analyze(jobs)
    interpolation_coefficient = parameters["interpolation_coefficient"]
    deterioratn_rate = parameters["deterioration_rate"]
    learning_percentage = parameters["learning_percentage"]

    learnng_rate = calculate_learning_coefficient(learning_percentage)  # öğrenme katsayısı hesaplanmaktadır.
    schedule_revised = calculate_schedule_by_PD(jobs, 1, 0, learnng_rate, deterioratn_rate,
                                                interpolation_coefficient)

    print("XXXXXXXXXXXXXXXXXXX")

    start_A = time.time()  # A ajanına yönelik en iyi çizelgenin bulunmasına başlama zamanı
    initial_solution_A_best = compose_schedule_A_best(schedule_revised, 0, 0, learnng_rate, deterioratn_rate,
                                                      interpolation_coefficient)  # A ajanının işlerini başlangıç çözüm
    # çizelgenin ilk sıralarına tardy şartlarına dikkat ederek atar.
    print(initial_solution_A_best)
    initial_solution_A_best_LB = calculate_object(initial_solution_A_best)["A amacı"]
    print("initial_solution_A_best_LB: {}".format(initial_solution_A_best_LB))
    branch_bound_A_best = branch_and_bounding_A_best(initial_solution_A_best, initial_solution_A_best_LB, learnng_rate,
                                                     deterioratn_rate)
    print("A AJANI İÇİN DAL SINIR SONUCU: {}".format(branch_bound_A_best))
    deviation_A_best = (branch_bound_A_best["A ajanı amac"] - initial_solution_A_best_LB) / initial_solution_A_best_LB
    print("dal sınır ie elde edilen sonuç başlangıç çözümden %{} daha iyi sonuç vermiştir.".format(deviation_A_best))
    elapsed_time_A_best = (time.time() - start_A)  # A ajanı en iyi değeri için algoritma süresi
    # 1 birim elapsed_time 1/100 seconda eşdeğerdir.
    #  with open('MAKALE-A-SONUC.csv', mode='w') as csv_file: eğer dosyayı ilk kez oluşturacak olsaydık bunu yazacaktık.
    with open('MAKALE-A-SONUC.csv', mode='a+', newline='') as csv_file:  # Create a writer object from csv module
        fieldnames = ['interpolation coefficient', 'learning rate', 'deterioration rate', 'number_of_A_jobs',
                      'number_of_B_jobs', 'toplam_node_sayısı', 'node_ratio', 'sapma', 'CPU_time', 'is_esneklik_medium',
                      'is_esneklik_max']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        #  writer.writeheader()  # ilk kez oluşturuken eklenecek olan header değerleri
        writer.writerow({'interpolation coefficient': interpolation_coefficient,
                         'learning rate': learning_percentage,
                         'deterioration rate': deterioratn_rate,
                         'number_of_A_jobs': len(A.job_list),
                         'number_of_B_jobs': len(B.job_list),
                         'toplam_node_sayısı': branch_bound_A_best["toplam_node_sayısı"],
                         "node_ratio": branch_bound_A_best["node_ratio"],
                         'sapma': deviation_A_best,
                         'CPU_time': elapsed_time_A_best,
                         'is_esneklik_medium': jobs_ratio["medium"],
                         'is_esneklik_max': jobs_ratio["max"]})

    print("XXXXXXXXXXXXXXXXXX")

    start_B = time.time()  # B ajanına yönelik en iyi çizelgenin bulunmasına başlama zamanı
    initial_solution_B_best = compose_schedule_B_best(initial_solution_A_best, 0, 0, learnng_rate, deterioratn_rate)
    # A ajnı için tardy joblar dikkate alınarak oluşturulmuş çizelgeden sadece B ajanı işlerinin sıralandığı çizelgedir.
    initial_solution_B_best_LB = calculate_object(initial_solution_B_best)["B amacı"]
    print("initial_solution_B_best_LB: {}".format(initial_solution_B_best_LB))
    branch_bound_B_best = branch_and_bounding_B_best(initial_solution_B_best, initial_solution_B_best_LB, learnng_rate,
                                                     deterioratn_rate)
    print("B AJANI İÇİN DAL SINIR SONUCU: {}".format(branch_bound_B_best))
    deviation_B_best = (branch_bound_B_best["B ajanı amac"] - initial_solution_B_best_LB) / initial_solution_B_best_LB
    print("dal sınır ie elde edilen sonuç başlangıç çözümden %{} daha iyi sonuç vermiştir.".format(deviation_B_best))
    elapsed_time_B_best = (time.time() - start_B)
    print("XXXXXXXXXXXXXXXXXX")

    if branch_bound_A_best["A ajanı amac"] < branch_bound_B_best["A ajanı amac"]:
        A_best = branch_bound_A_best["A ajanı amac"]
        A_worst = branch_bound_B_best["A ajanı amac"]
    else:
        A_worst = branch_bound_A_best["A ajanı amac"]
        A_best = branch_bound_B_best["A ajanı amac"]
    if branch_bound_B_best["B ajanı amac"] < branch_bound_A_best["B ajanı amac"]:
        B_best = branch_bound_B_best["B ajanı amac"]
        B_worst = branch_bound_A_best["B ajanı amac"]
    else:
        B_worst = branch_bound_B_best["B ajanı amac"]
        B_best = branch_bound_A_best["B ajanı amac"]

    print("A best: {}, B best {}, A worst {}, B worst {}".format(A_best, B_best, A_worst, B_worst))
    schedule_revised_all_agents = calculate_schedule_by_PD_all_agents_adjusted_weights(all_jobs, 1, 0, A_best, B_best,
                                                                                       A_worst, B_worst, learnng_rate,
                                                                                       deterioratn_rate)
    initial_solution = compose_schedule_all_agents(schedule_revised_all_agents, A_best, B_best, A_worst, B_worst,
                                                   learnng_rate, deterioratn_rate)
    initial_solution_object = calculate_object(initial_solution)
    if A_best != A_worst and B_best != B_worst:
        lower_bound = all_amac(initial_solution_object["A amacı"], initial_solution_object["B amacı"],
                               A_best, B_best, A_worst, B_worst)
        print(" çizelge A amacı {}  B amacı {} ve lower_bound değeri {}"
              .format(initial_solution_object["A amacı"], initial_solution_object["B amacı"], lower_bound))
        branch_bound_all_agenst = branch_and_bounding_all_agents(initial_solution, lower_bound, A_best, B_best, A_worst,
                                                                 B_worst, learnng_rate, deterioratn_rate)
        deviation_all_agenst = (branch_bound_all_agenst["cizelge amac"] - lower_bound) / lower_bound
    else:
        deviation_all_agenst = 0
        branch_bound_all_agenst = {"toplam_node_sayısı": 0, "node_ratio": 0}

    elapsed_time_all_agents = (time.time() - start_A)
    #  with open('MAKALE-ALL-SONUC.csv', mode='w') as csv_file:
    with open('MAKALEA-ALL-SONUC.csv', mode='a+', newline='') as csv_file:  # Create a writer object from csv module
        fieldnames = ['interpolation coefficient', 'learning rate', 'deterioration rate',
                      'number_of_A_jobs', 'number_of_B_jobs',
                      'A_best_toplam_node_sayısı', 'A_best_node_ratio', 'A_best_sapma', 'A_best_CPU_time',
                      'B_best_toplam_node_sayısı', 'B_best_node_ratio', 'B_best_sapma', 'B_best_CPU_time',
                      'all_agents_toplam_node_sayısı', 'all_agents_node_ratio', 'all_agents_sapma',
                      'all_agents_CPU_time',
                      'is_esneklik_medium', 'is_esneklik_max'
                      ]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        #  writer.writeheader()  # ilk kez oluşturuken eklenecek olan header değerleri
        writer.writerow({'interpolation coefficient': interpolation_coefficient,
                         'learning rate': learning_percentage,
                         'deterioration rate': deterioratn_rate,
                         'number_of_A_jobs': len(A.job_list),
                         'number_of_B_jobs': len(B.job_list),
                         'A_best_toplam_node_sayısı': branch_bound_A_best["toplam_node_sayısı"],
                         "A_best_node_ratio": branch_bound_A_best["node_ratio"],
                         'A_best_sapma': deviation_A_best,
                         'A_best_CPU_time': elapsed_time_A_best,
                         'B_best_toplam_node_sayısı': branch_bound_B_best["toplam_node_sayısı"],
                         "B_best_node_ratio": branch_bound_B_best["node_ratio"],
                         'B_best_sapma': deviation_B_best,
                         'B_best_CPU_time': elapsed_time_B_best,
                         'all_agents_toplam_node_sayısı': branch_bound_all_agenst["toplam_node_sayısı"],
                         "all_agents_node_ratio": branch_bound_all_agenst["node_ratio"],
                         'all_agents_sapma': deviation_all_agenst,
                         'all_agents_CPU_time': elapsed_time_all_agents,
                         'is_esneklik_medium': jobs_ratio["medium"],
                         'is_esneklik_max': jobs_ratio["max"]})


parameters_1 = {"interpolation_coefficient": 0.5, "deterioration_rate": 0.2, "learning_percentage": 0.8}
parameters_2 = {"interpolation_coefficient": 0, "deterioration_rate": 0.2, "learning_percentage": 0.8}
parameters_3 = {"interpolation_coefficient": 1, "deterioration_rate": 0.2, "learning_percentage": 0.8}
parameters_4 = {"interpolation_coefficient": 0.5, "deterioration_rate": 0.1, "learning_percentage": 0.8}
parameters_5 = {"interpolation_coefficient": 0, "deterioration_rate": 0.1, "learning_percentage": 0.8}
parameters_6 = {"interpolation_coefficient": 1, "deterioration_rate": 0.1, "learning_percentage": 0.8}
parameters_7 = {"interpolation_coefficient": 0.5, "deterioration_rate": 0.2, "learning_percentage": 0.7}
parameters_8 = {"interpolation_coefficient": 0, "deterioration_rate": 0.2, "learning_percentage": 0.7}
parameters_9 = {"interpolation_coefficient": 1, "deterioration_rate": 0.2, "learning_percentage": 0.7}
parameters_10 = {"interpolation_coefficient": 0.5, "deterioration_rate": 0.1, "learning_percentage": 0.7}
parameters_11 = {"interpolation_coefficient": 0, "deterioration_rate": 0.1, "learning_percentage": 0.7}
parameters_12 = {"interpolation_coefficient": 1, "deterioration_rate": 0.1, "learning_percentage": 0.7}
parameters_13 = {"interpolation_coefficient": 0.5, "deterioration_rate": 0.2, "learning_percentage": 0.9}
parameters_14 = {"interpolation_coefficient": 0, "deterioration_rate": 0.2, "learning_percentage": 0.9}
parameters_15 = {"interpolation_coefficient": 1, "deterioration_rate": 0.2, "learning_percentage": 0.9}
parameters_16 = {"interpolation_coefficient": 0.5, "deterioration_rate": 0.1, "learning_percentage": 0.9}
parameters_17 = {"interpolation_coefficient": 0, "deterioration_rate": 0.1, "learning_percentage": 0.9}
parameters_18 = {"interpolation_coefficient": 1, "deterioration_rate": 0.1, "learning_percentage": 0.9}

""" Proje two agent problemi olduğundan 2 ajan tanımlanacaktır."""
A = Agents("A")
B = Agents("B")
all_jobs = jobs_info()  # çizelgelenmesi istenen işlere ait bilgiler oluşturulmaktadır.
#functions_all_A_best(all_jobs, parameters_13)
#functions_all_A_best(all_jobs, parameters_14)
#functions_all_A_best(all_jobs, parameters_15)
#functions_all_A_best(all_jobs, parameters_16)
#functions_all_A_best(all_jobs, parameters_17)
#functions_all_A_best(all_jobs, parameters_18)
functions_all_A_best(all_jobs, parameters_1)
#functions_all_A_best(all_jobs, parameters_2)
#functions_all_A_best(all_jobs, parameters_3)
#functions_all_A_best(all_jobs, parameters_4)
#functions_all_A_best(all_jobs, parameters_5)
#functions_all_A_best(all_jobs, parameters_6)
#functions_all_A_best(all_jobs, parameters_7)
#functions_all_A_best(all_jobs, parameters_8)
#functions_all_A_best(all_jobs, parameters_9)
#functions_all_A_best(all_jobs, parameters_10)
#functions_all_A_best(all_jobs, parameters_11)
#functions_all_A_best(all_jobs, parameters_12)

"""
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
data = pd.read_csv('MAKALE-A-SONUC.csv', sep=',', na_values='.')
datason = pd.read_csv('MAKALE-5.csv', sep=';', na_values='.')
datason2 = pd.read_csv('MAKALE-15.csv', sep=';', na_values='.')
# sum_column = data['number_of_A_jobs'] + data['number_of_B_jobs']
# data["col3"] = sum_column
#number_data = data.groupby("col3")
#number_data.boxplot(column=['node_ratio'])

#datason.boxplot(by ='toplam_is_sayisi', column=['node_ratio'], grid = False)
#datason.boxplot(by ='toplam_is_sayisi', column=['CPU_time'], grid = False)
# datason.boxplot(column=['sapma'])
plt.show()


def get_summary_statistics(dataset):
    mean = np.round(np.mean(dataset), 10)
    median = np.round(np.median(dataset), 10)
    min_value = np.round(dataset.min(), 10)
    max_value = np.round(dataset.max(), 10)
    quartile_1 = np.round(dataset.quantile(0.25), 10)
    quartile_3 = np.round(dataset.quantile(0.75), 10)
    # Interquartile range
    iqr = np.round(quartile_3 - quartile_1, 10)
    print('Min: %s' % min_value)
    print('Mean: %s' % mean)
    print('Max: %s' % max_value)
    print('25th percentile: %s' % quartile_1)
    print('Median: %s' % median)
    print('75th percentile: %s' % quartile_3)
    print('Interquartile range (IQR): %s' % iqr)


print('\n\nToplam iş sayısı 5 için sapma değerleri summary statistics')
get_summary_statistics(datason["sapma"])
print("")
print('\n\nToplam iş sayısı 5 için CPU_time değerleri summary statistics')
get_summary_statistics(datason["CPU_time"])
print("")
print('\n\nToplam iş sayısı 5 için node_ratio değerleri summary statistics')
get_summary_statistics(datason["node_ratio"])
print("")
print('\n\nToplam iş sayısı 15 için sapma değerleri summary statistics')
get_summary_statistics(datason2["sapma"])
print("")
print('\n\nToplam iş sayısı 15 için CPU_time değerleri summary statistics')
get_summary_statistics(datason2["CPU_time"])
print("")
print('\n\nToplam iş sayısı 15 için node_ratio değerleri summary statistics')
get_summary_statistics(datason2["node_ratio"])
print("")"""
