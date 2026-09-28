import os
import random
import json
import threading
from datetime import datetime, timedelta
from locust import HttpUser, task, between, tag, events
from locust.exception import StopUser

CONFIG = {
    "BASE_URL": os.getenv("LOCUST_BASE_URL", "http://localhost:8000"),
    "MIN_WAIT": int(os.getenv("LOCUST_MIN_WAIT", 1000)),
    "MAX_WAIT": int(os.getenv("LOCUST_MAX_WAIT", 3000)),
    "USERNAME": os.getenv("LOCUST_USERNAME", "admin"),
    "PASSWORD": os.getenv("LOCUST_PASSWORD", "admin"),
    "ENABLE_LOGIN": os.getenv("LOCUST_ENABLE_LOGIN", "false").lower() == "true",
    "MAX_REQUESTS_PER_USER": int(os.getenv("LOCUST_MAX_REQUESTS", 100)),
    "TEST_DATA": {
        "client_names": ["客户A", "客户B", "客户C", "客户D", "客户E", "云南朝锐仪器有限公司", "fokhrul", "tanvir"],
        "product_models": ["产品A", "产品B", "产品C", "产品D", "产品E"],
        "project_managers": ["张三", "李四", "王五", "赵六", "钱七"],
        "trial_periods": ["7天", "15天", "30天", "45天", "60天"],
        "status_values": ["not_due", "due", "over_due"],
    }
}

REPORT_DATA = {
    "total_requests": 0,
    "successful_requests": 0,
    "failed_requests": 0,
    "response_times": [],
    "errors": [],
    "start_time": None,
}
_REPORT_LOCK = threading.Lock()


def generate_test_data():
    return {
        "client_name": random.choice(CONFIG["TEST_DATA"]["client_names"]),
        "project_manager": random.choice(CONFIG["TEST_DATA"]["project_managers"]),
        "product_model": random.choice(CONFIG["TEST_DATA"]["product_models"]),
        "trial_period_days": random.choice(CONFIG["TEST_DATA"]["trial_periods"]),
        "trial_start_date": (datetime.now() - timedelta(days=random.randint(1, 90))).strftime("%Y-%m-%d"),
        "contract_no": f"CN{random.randint(1000, 9999)}",
        "sn": f"SN{random.randint(100000, 999999)}",
        "quantity": random.randint(1, 10),
    }


def generate_aftersales_data():
    return {
        "product_name": random.choice(CONFIG["TEST_DATA"]["product_models"]),
        "client_name": random.choice(CONFIG["TEST_DATA"]["client_names"]),
        "issue_description": f"测试问题描述 {random.randint(1, 1000)}",
        "status": random.choice(["pending", "processing", "resolved"]),
    }


@events.request.add_listener
def request_stats(**kwargs):
    with _REPORT_LOCK:
        REPORT_DATA["total_requests"] += 1
        if kwargs["response_time"] is not None:
            REPORT_DATA["response_times"].append(kwargs["response_time"])
        if kwargs["exception"]:
            REPORT_DATA["failed_requests"] += 1
            error_info = {
                "time": datetime.now().isoformat(),
                "url": kwargs["request_type"] + " " + kwargs["name"],
                "error": str(kwargs["exception"]),
            }
            if len(REPORT_DATA["errors"]) < 100:
                REPORT_DATA["errors"].append(error_info)
        else:
            REPORT_DATA["successful_requests"] += 1


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    with _REPORT_LOCK:
        REPORT_DATA["start_time"] = datetime.now()
        REPORT_DATA["total_requests"] = 0
        REPORT_DATA["successful_requests"] = 0
        REPORT_DATA["failed_requests"] = 0
        REPORT_DATA["response_times"] = []
        REPORT_DATA["errors"] = []
    
    print(f"\n{'='*60}")
    print(f"LOAD TEST STARTED - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")
    print(f"Base URL: {CONFIG['BASE_URL']}")
    print(f"Login Enabled: {CONFIG['ENABLE_LOGIN']}")
    print(f"Max Requests per User: {CONFIG['MAX_REQUESTS_PER_USER']}")
    print(f"Wait Time: {CONFIG['MIN_WAIT']}-{CONFIG['MAX_WAIT']}ms")
    print(f"{'='*60}\n")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    with _REPORT_LOCK:
        start_time = REPORT_DATA["start_time"]
        total_requests = REPORT_DATA["total_requests"]
        successful_requests = REPORT_DATA["successful_requests"]
        failed_requests = REPORT_DATA["failed_requests"]
        response_times = REPORT_DATA["response_times"].copy()
        errors = REPORT_DATA["errors"].copy()
    
    if start_time:
        duration = datetime.now() - start_time
    else:
        duration = timedelta(seconds=0)
    
    avg_response_time = sum(response_times) / len(response_times) if response_times else 0
    p95_response_time = 0
    p99_response_time = 0
    if response_times:
        sorted_times = sorted(response_times)
        p95_idx = int(len(sorted_times) * 0.95)
        p99_idx = int(len(sorted_times) * 0.99)
        p95_response_time = sorted_times[p95_idx] if p95_idx < len(sorted_times) else 0
        p99_response_time = sorted_times[p99_idx] if p99_idx < len(sorted_times) else 0
    
    success_rate = (successful_requests / total_requests) * 100 if total_requests else 0

    print(f"\n{'='*60}")
    print(f"LOAD TEST REPORT - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")
    print(f"Duration: {duration.total_seconds():.2f} seconds")
    print(f"Total Requests: {total_requests}")
    print(f"Successful Requests: {successful_requests}")
    print(f"Failed Requests: {failed_requests}")
    print(f"Success Rate: {success_rate:.2f}%")
    print(f"Average Response Time: {avg_response_time:.2f}ms")
    print(f"P95 Response Time: {p95_response_time:.2f}ms")
    print(f"P99 Response Time: {p99_response_time:.2f}ms")
    
    if errors:
        print(f"\nTop Errors ({min(5, len(errors))}):")
        for i, error in enumerate(errors[:5], 1):
            print(f"  {i}. [{error['time']}] {error['url']}")
            print(f"     Error: {error['error']}")
    
    report_file = f"load_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    report_content = {
        "start_time": start_time.isoformat() if start_time else None,
        "end_time": datetime.now().isoformat(),
        "duration_seconds": duration.total_seconds(),
        "config": CONFIG,
        "metrics": {
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "success_rate": success_rate,
            "avg_response_time_ms": avg_response_time,
            "p95_response_time_ms": p95_response_time,
            "p99_response_time_ms": p99_response_time,
        },
        "errors": errors,
    }
    
    try:
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report_content, f, ensure_ascii=False, indent=2)
        print(f"\nReport saved to: {report_file}")
    except Exception as e:
        print(f"\nFailed to save report: {str(e)}")
    
    print(f"{'='*60}")


class BaseUser(HttpUser):
    abstract = True
    host = CONFIG["BASE_URL"]
    
    def on_start(self):
        self.request_count = 0
        self.logged_in = False
        if CONFIG["ENABLE_LOGIN"]:
            self.login()
    
    def on_stop(self):
        if CONFIG["ENABLE_LOGIN"] and self.logged_in:
            self.logout()
    
    def login(self):
        try:
            response = self.client.post(
                "/login/",
                data={"username": CONFIG["USERNAME"], "password": CONFIG["PASSWORD"]},
                catch_response=True,
                name="Login"
            )
            if response.status_code in [200, 302]:
                response.success()
                self.logged_in = True
            else:
                response.failure(f"Login failed with status {response.status_code}")
                self.logged_in = False
        except Exception as e:
            self.logged_in = False
            print(f"Login error: {str(e)}")
    
    def logout(self):
        try:
            self.client.get("/logout/", name="Logout")
        except Exception:
            pass
    
    def check_max_requests(self):
        self.request_count += 1
        if self.request_count >= CONFIG["MAX_REQUESTS_PER_USER"]:
            raise StopUser(f"Reached max requests ({CONFIG['MAX_REQUESTS_PER_USER']})")


class HomeUser(BaseUser):
    wait_time = between(CONFIG["MIN_WAIT"] / 1000, CONFIG["MAX_WAIT"] / 1000)
    
    @tag("home", "browse")
    @task(3)
    def view_home(self):
        self.client.get("/", name="Home Page")
        self.check_max_requests()
    
    @tag("home", "about")
    @task(1)
    def view_about(self):
        self.client.get("/about/", name="About Page")
        self.check_max_requests()


class TrialItemUser(BaseUser):
    wait_time = between(CONFIG["MIN_WAIT"] / 1000, CONFIG["MAX_WAIT"] / 1000)
    
    @tag("trialitem", "list")
    @task(5)
    def view_trialitem_list(self):
        self.client.get("/trial-item/", name="Trial Item List")
        self.check_max_requests()
    
    @tag("trialitem", "detail")
    @task(3)
    def view_trialitem_detail(self):
        pk = random.randint(1, 50)
        with self.client.get(f"/trial-item/detail/{pk}/", name="Trial Item Detail", catch_response=True) as response:
            if response.status_code == 404:
                response.success()
        self.check_max_requests()
    
    @tag("trialitem", "create")
    @task(2)
    def create_trialitem(self):
        data = generate_test_data()
        with self.client.post(
            "/trial-item/create/",
            data=data,
            name="Create Trial Item",
            catch_response=True
        ) as response:
            if response.status_code in [200, 302]:
                response.success()
            else:
                response.failure(f"Create failed with status {response.status_code}")
        self.check_max_requests()
    
    @tag("trialitem", "update")
    @task(2)
    def update_trialitem(self):
        pk = random.randint(1, 50)
        data = generate_test_data()
        with self.client.post(
            f"/trial-item/update/{pk}/",
            data=data,
            name="Update Trial Item",
            catch_response=True
        ) as response:
            if response.status_code in [200, 302]:
                response.success()
            else:
                response.failure(f"Update failed with status {response.status_code}")
        self.check_max_requests()
    
    @tag("trialitem", "export")
    @task(1)
    def export_trialitem(self):
        self.client.get("/trial-item/export/", name="Export Trial Items")
        self.check_max_requests()


class ProductUser(BaseUser):
    wait_time = between(CONFIG["MIN_WAIT"] / 1000, CONFIG["MAX_WAIT"] / 1000)
    
    @tag("product", "list")
    @task(5)
    def view_product_list(self):
        self.client.get("/product/", name="Product List")
        self.check_max_requests()
    
    @tag("product", "detail")
    @task(3)
    def view_product_detail(self):
        pk = random.randint(1, 50)
        with self.client.get(f"/product/{pk}/", name="Product Detail", catch_response=True) as response:
            if response.status_code == 404:
                response.success()
        self.check_max_requests()
    
    @tag("product", "create")
    @task(2)
    def create_product(self):
        data = generate_aftersales_data()
        with self.client.post(
            "/product/create/",
            data=data,
            name="Create Product",
            catch_response=True
        ) as response:
            if response.status_code in [200, 302]:
                response.success()
            else:
                response.failure(f"Create failed with status {response.status_code}")
        self.check_max_requests()
    
    @tag("product", "update")
    @task(2)
    def update_product(self):
        pk = random.randint(1, 50)
        data = generate_aftersales_data()
        with self.client.post(
            f"/product/{pk}/edit/",
            data=data,
            name="Update Product",
            catch_response=True
        ) as response:
            if response.status_code in [200, 302]:
                response.success()
            else:
                response.failure(f"Update failed with status {response.status_code}")
        self.check_max_requests()
    
    @tag("product", "export")
    @task(1)
    def export_product(self):
        self.client.get("/product/export/", name="Export Products")
        self.check_max_requests()


class MixedLoadUser(BaseUser):
    wait_time = between(CONFIG["MIN_WAIT"] / 1000, CONFIG["MAX_WAIT"] / 1000)
    
    @tag("mixed", "home")
    @task(2)
    def view_home(self):
        self.client.get("/", name="Home Page")
        self.check_max_requests()
    
    @tag("mixed", "trialitem")
    @task(3)
    def view_trialitem_list(self):
        self.client.get("/trial-item/", name="Trial Item List")
        self.check_max_requests()
    
    @tag("mixed", "product")
    @task(3)
    def view_product_list(self):
        self.client.get("/product/", name="Product List")
        self.check_max_requests()
    
    @tag("mixed", "create")
    @task(1)
    def create_trialitem(self):
        data = generate_test_data()
        with self.client.post(
            "/trial-item/create/",
            data=data,
            name="Create Trial Item (Mixed)",
            catch_response=True
        ) as response:
            if response.status_code in [200, 302]:
                response.success()
            else:
                response.failure(f"Create failed with status {response.status_code}")
        self.check_max_requests()
    
    @tag("mixed", "export")
    @task(1)
    def export_data(self):
        if random.choice([True, False]):
            self.client.get("/trial-item/export/", name="Export Trial Items (Mixed)")
        else:
            self.client.get("/product/export/", name="Export Products (Mixed)")
        self.check_max_requests()
