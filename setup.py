from setuptools import setup, find_packages

# 메인 서버 구동 시 setup()이 자동 실행되는 것을 방지합니다.
if __name__ == '__main__':
    setup(
        name='addrhide',
        version='1.0.0',
        description='M3U API Key Hiding Proxy Plugin',
        packages=find_packages(),
        include_package_data=True,
        install_requires=[
            'requests',
            'flask'
        ],
    )
